from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    prompt: str
    history: List[ChatMessage] = []
    context: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
