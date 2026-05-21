from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_memory import UserMemory


class MemoryRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_user_id(self, user_id: int) -> UserMemory | None:
        stmt = select(UserMemory).where(UserMemory.user_id == user_id)
        return self._db.scalars(stmt).first()
