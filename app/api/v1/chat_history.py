"""API endpoints for chat session CRUD and message persistence."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.auth import get_current_user
from app.core.logging import setup_logger
from app.db.deps import get_db
from app.schemas.chat_history import (
    CreateSessionRequest,
    SessionSummary,
    SessionDetail,
    AddMessageRequest,
    MessageOut,
)
from app.services.chat_history_service import ChatHistoryService

logger = setup_logger(__name__, log_file="logs/chat_history.log")
router = APIRouter(prefix="/chats", tags=["Chat History"])

history_service = ChatHistoryService()


# ---------- Sessions ----------

@router.post("", response_model=SessionSummary, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new chat session for the current user."""
    title = body.title or "New Chat"
    session = history_service.create_session(db, user_id=current_user.id, title=title)
    return session


@router.get("", response_model=List[SessionSummary])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all chat sessions of the current user (newest first)."""
    return history_service.list_sessions(db, user_id=current_user.id)


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Load a chat session with all its messages."""
    session = history_service.get_session(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.patch("/{session_id}", response_model=SessionSummary)
async def update_session_title(
    session_id: UUID,
    body: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rename a chat session."""
    if not body.title:
        raise HTTPException(status_code=400, detail="Title is required")
    session = history_service.update_title(db, session_id=session_id, user_id=current_user.id, title=body.title)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a chat session and all its messages."""
    deleted = history_service.delete_session(db, session_id=session_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat session not found")


# ---------- Messages ----------

@router.post("/{session_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def add_message(
    session_id: UUID,
    body: AddMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Append a message to an existing session."""
    # Verify the session belongs to this user
    session = history_service.get_session(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    if body.role not in ("user", "assistant"):
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'assistant'")

    msg = history_service.add_message(db, session_id=session_id, role=body.role, content=body.content)
    return msg


@router.get("/{session_id}/messages", response_model=List[MessageOut])
async def list_messages(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all messages for a session."""
    session = history_service.get_session(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return history_service.get_messages(db, session_id=session_id)
