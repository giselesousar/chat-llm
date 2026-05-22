from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_session_by_public_id(self, session_id: str, *, user_id: int) -> ChatSession | None:
        stmt = select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
        )
        return self._db.scalars(stmt).first()

    def create_session(self, *, session_id: str, user_id: int, channel: str) -> ChatSession:
        session = ChatSession(session_id=session_id, user_id=user_id, channel=channel)
        self._db.add(session)
        self._db.flush()
        return session

    def list_recent_messages(
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

    def add_message(self, *, session_pk: int, role: str, content: str) -> ChatMessage:
        message = ChatMessage(session_id=session_pk, role=role, content=content)
        self._db.add(message)
        self._db.flush()
        return message

    def list_sessions_by_user(self, user_id: int) -> list[ChatSession]:
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return list(self._db.scalars(stmt).all())

    def delete_session(self, session: ChatSession) -> None:
        for msg in list(session.messages):
            self._db.delete(msg)
        self._db.delete(session)

    def list_messages(
        self,
        session_pk: int,
        *,
        limit: int | None = None,
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_pk)
            .order_by(ChatMessage.created_at.asc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self._db.scalars(stmt).all())
