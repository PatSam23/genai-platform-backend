from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.providers.ollama import OllamaProvider

router = APIRouter(tags=["Chat"])

llm = OllamaProvider()


class ChatRequest(BaseModel):
    prompt: str
    context: Optional[str] = None  # future RAG support


@router.post("/chat")
async def chat(request: ChatRequest):
    response = await llm.generate(
        prompt=request.prompt,
        context=request.context
    )
    return {
        "response": response
    }
