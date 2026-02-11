from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import json

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/chat.log")
router = APIRouter(tags=["Chat"])
chat_service = ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Chat request received - prompt length: {len(request.prompt)}, history messages: {len(request.history)}")
    try:
        response = await chat_service.generate(
            prompt=request.prompt,
            history=request.history,
            context=request.context,
        )
        logger.info(f"Chat response generated - response length: {len(response)}")
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error generating chat response: {str(e)}", exc_info=True)
        raise


@router.post("/chat/stream")
async def chat_stream(request: Request, payload: ChatRequest):
    logger.info(f"Streaming chat request received - prompt length: {len(payload.prompt)}")
    
    async def event_generator():
        token_count = 0
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
                yield "data: " + json.dumps({
                    "type": "token",
                    "value": token,
                }) + "\n\n"

            logger.info(f"Streaming completed - tokens generated: {token_count}")
            yield "data: " + json.dumps({"type": "done"}) + "\n\n"
        except Exception as e:
            logger.error(f"Error during streaming: {str(e)}", exc_info=True)
            yield "data: " + json.dumps({"type": "error", "message": "Internal error"}) + "\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
