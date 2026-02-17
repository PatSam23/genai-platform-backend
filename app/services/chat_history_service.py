"""Service layer for chat session / message CRUD."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.chat_history import ChatSession, ChatMessageDB
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/chat_history.log")


class ChatHistoryService:

    # ------ Sessions ------

    @staticmethod
    def create_session(db: Session, user_id: int, title: str = "New Chat") -> ChatSession:
        session = ChatSession(user_id=user_id, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Created chat session {session.id} for user {user_id}")
        return session

    @staticmethod
    def list_sessions(db: Session, user_id: int) -> List[ChatSession]:
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .all()
        )

    @staticmethod
    def get_session(db: Session, session_id: UUID, user_id: int) -> Optional[ChatSession]:
        return (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )

    @staticmethod
    def update_title(db: Session, session_id: UUID, user_id: int, title: str) -> Optional[ChatSession]:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
        if session:
            session.title = title
            session.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: UUID, user_id: int) -> bool:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
        if not session:
            return False
        db.delete(session)
        db.commit()
        logger.info(f"Deleted chat session {session_id}")
        return True

    # ------ Messages ------

    @staticmethod
    def add_message(db: Session, session_id: UUID, role: str, content: str, file_name: str | None = None) -> ChatMessageDB:
        msg = ChatMessageDB(session_id=session_id, role=role, content=content, file_name=file_name)
        db.add(msg)
        # Also bump updated_at on the session
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_messages(db: Session, session_id: UUID) -> List[ChatMessageDB]:
        return (
            db.query(ChatMessageDB)
            .filter(ChatMessageDB.session_id == session_id)
            .order_by(ChatMessageDB.created_at.asc())
            .all()
        )
