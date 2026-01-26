from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.ai_service import AIService

router = APIRouter(tags=["Chat"])

ai_service = AIService()

class ChatRequest(BaseModel):
    prompt: str
    context: Optional[str] = None  # future RAG support


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint using AIService for prompt orchestration and provider invocation.
    """
    response = await ai_service.chat(user_message=request.prompt, rag_context=request.context)
    return {"response": response}
