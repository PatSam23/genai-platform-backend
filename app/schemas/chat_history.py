"""Pydantic schemas for chat history API requests/responses."""

from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel


# ---------- Request ----------

class CreateSessionRequest(BaseModel):
    title: Optional[str] = None  # Optional — backend may auto-generate via AI


class AddMessageRequest(BaseModel):
    role: str  # "user" | "assistant"
    content: str


# ---------- Response ----------

class MessageOut(BaseModel):
    id: UUID
    role: str
    content: str
    file_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionSummary(BaseModel):
    """Lightweight object shown in the sidebar list."""
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionDetail(BaseModel):
    """Full session with messages — used when opening a chat."""
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut] = []

    model_config = {"from_attributes": True}
