from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    prompt: str
    history: List[ChatMessage] = []
    context: Optional[str] = None
    session_id: Optional[str] = None  # UUID string — links to persisted chat session


class ChatResponse(BaseModel):
    response: str
