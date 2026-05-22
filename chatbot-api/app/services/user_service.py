from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import UsernameAlreadyExistsError
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegisterRequest


class UserService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = UserRepository(db)

    def register(self, payload: UserRegisterRequest) -> User:
        user = self._repo.create(
            username=payload.username,
            hashed_password=get_password_hash(payload.password),
        )
        try:
            self._db.commit()
            self._db.refresh(user)
            return user
        except IntegrityError as exc:
            self._db.rollback()
            raise UsernameAlreadyExistsError(payload.username) from exc

    def authenticate(self, username: str, password: str) -> User | None:
        user = self._repo.get_by_username(username)
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
