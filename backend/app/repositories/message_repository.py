from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage


class MessageRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_recent_for_session(
        self,
        session_pk: int,
        *,
        limit: int,
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_pk)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        rows = list(self._db.scalars(stmt).all())
        rows.reverse()
        return rows

    def add(self, *, session_pk: int, role: str, content: str) -> ChatMessage:
        message = ChatMessage(session_id=session_pk, role=role, content=content)
        self._db.add(message)
        self._db.flush()
        return message
