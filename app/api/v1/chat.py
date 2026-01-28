from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.services.ai_service import AIService

router = APIRouter(tags=["Chat"])
ai_service = AIService()


class ChatRequest(BaseModel):
    prompt: str
    context: Optional[str] = None


@router.post("/chat")
async def chat(request: ChatRequest):
    response = await ai_service.generate_response(
        request.prompt, request.context
    )
    return {"response": response}


@router.post("/chat/stream")
async def chat_stream(request: Request, payload: ChatRequest):
    async def event_generator():
        async for token in ai_service.stream_response(
            payload.prompt, payload.context
        ):
            if await request.is_disconnected():
                print("Client disconnected, stopping stream")
                break

            yield f"data: {token}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )