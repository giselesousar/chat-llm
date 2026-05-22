from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self._db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self._db.scalars(stmt).first()

    def create(self, *, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)
        self._db.add(user)
        self._db.flush()
        return user
