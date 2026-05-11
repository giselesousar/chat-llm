from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db import get_db
from app.models.user import User
from app.providers.ollama_provider import OllamaProvider
from app.services.user_service import UserService


def get_ollama_provider() -> OllamaProvider:
    return OllamaProvider()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


OllamaProviderDep = Annotated[OllamaProvider, Depends(get_ollama_provider)]
DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
