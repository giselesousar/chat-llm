import uuid

from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession
from app.repositories.session_repository import SessionRepository


class ChatSessionService:
    def __init__(self, db: Session) -> None:
        self._repo = SessionRepository(db)

    def resolve(
        self,
        *,
        user_id: int,
        session_id: str | None,
        channel: str,
    ) -> ChatSession:
        if session_id:
            existing = self._repo.get_by_public_id(session_id, user_id=user_id)
            if existing is not None:
                return existing
        public_id = session_id or str(uuid.uuid4())
        return self._repo.create(session_id=public_id, user_id=user_id, channel=channel)
