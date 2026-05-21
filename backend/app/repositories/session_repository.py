from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_public_id(self, session_id: str, *, user_id: int) -> ChatSession | None:
        stmt = select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
        )
        return self._db.scalars(stmt).first()

    def create(self, *, session_id: str, user_id: int, channel: str) -> ChatSession:
        session = ChatSession(session_id=session_id, user_id=user_id, channel=channel)
        self._db.add(session)
        self._db.flush()
        return session
