from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession
import json
from uuid import UUID

from app.models.chat import ChatRequest, ChatResponse
from app.models.user import User
from app.services.chat_service import ChatService
from app.services.chat_history_service import ChatHistoryService
from app.core.logging import setup_logger
from app.core.auth import get_current_user
from app.db.deps import get_db

logger = setup_logger(__name__, log_file="logs/chat.log")
router = APIRouter(tags=["Chat"])
chat_service = ChatService()
history_service = ChatHistoryService()


def _ensure_session(db: DBSession, user_id: int, session_id: str | None, prompt: str):
    """Return an existing session or create a new one. Returns (session_obj, session_id_str)."""
    if session_id:
        sid = UUID(session_id)
        session = history_service.get_session(db, session_id=sid, user_id=user_id)
        if session:
            return session, session_id
    # Auto-create with prompt snippet as title
    title = prompt[:80].strip() or "New Chat"
    session = history_service.create_session(db, user_id=user_id, title=title)
    return session, str(session.id)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    logger.info(f"Chat request from user {current_user.email} - prompt length: {len(request.prompt)}, history messages: {len(request.history)}")
    try:
        # Persist user message
        session_obj, sid = _ensure_session(db, current_user.id, request.session_id, request.prompt)
        history_service.add_message(db, session_id=session_obj.id, role="user", content=request.prompt)

        response = await chat_service.generate(
            prompt=request.prompt,
            history=request.history,
            context=request.context,
        )

        # Persist assistant message
        history_service.add_message(db, session_id=session_obj.id, role="assistant", content=response)

        logger.info(f"Chat response generated - response length: {len(response)}")
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error generating chat response: {str(e)}", exc_info=True)
        raise


@router.post("/chat/stream")
async def chat_stream(
    request: Request, 
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    logger.info(f"Streaming chat request from user {current_user.email} - prompt length: {len(payload.prompt)}")

    # Persist user message & resolve session
    session_obj, sid = _ensure_session(db, current_user.id, payload.session_id, payload.prompt)
    history_service.add_message(db, session_id=session_obj.id, role="user", content=payload.prompt)

    async def event_generator():
        token_count = 0
        full_response = []
        try:
            async for token in chat_service.stream(
                payload.prompt,
                payload.history,
                payload.context,
            ):
                if await request.is_disconnected():
                    logger.warning("Client disconnected during streaming")
                    break

                token_count += 1
                full_response.append(token)
                yield "data: " + json.dumps({
                    "type": "token",
                    "value": token,
                }) + "\n\n"

            logger.info(f"Streaming completed - tokens generated: {token_count}")
            
            # Persist the complete assistant response
            assistant_text = "".join(full_response)
            if assistant_text:
                history_service.add_message(db, session_id=session_obj.id, role="assistant", content=assistant_text)

            yield "data: " + json.dumps({"type": "done", "session_id": sid}) + "\n\n"
        except Exception as e:
            logger.error(f"Error during streaming: {str(e)}", exc_info=True)
            # Still try to persist partial response
            partial = "".join(full_response)
            if partial:
                history_service.add_message(db, session_id=session_obj.id, role="assistant", content=partial)
            yield "data: " + json.dumps({"type": "error", "message": "Internal error"}) + "\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
