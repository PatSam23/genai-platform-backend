from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import json

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["Chat"])
chat_service = ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = await chat_service.generate(
        prompt=request.prompt,
        history=request.history,
        context=request.context,
    )
    return ChatResponse(response=response)


@router.post("/chat/stream")
async def chat_stream(request: Request, payload: ChatRequest):
    async def event_generator():
        async for token in chat_service.stream(
            payload.prompt,
            payload.history,
            payload.context,
        ):
            if await request.is_disconnected():
                break

            yield "data: " + json.dumps({
                "type": "token",
                "value": token,
            }) + "\n\n"

        yield "data: " + json.dumps({"type": "done"}) + "\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
