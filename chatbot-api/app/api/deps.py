from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.services.chat_service import ChatService
from app.clients.inference_gateway import InferenceGateway
from app.clients.inference_client import InferenceHttpClient
from app.core.security import get_current_user
from app.db import get_db
from app.models.user import User
from app.services.user_service import UserService


def get_inference_gateway() -> InferenceGateway:
    return InferenceGateway(InferenceHttpClient())


def get_chat_service(
    db: Session = Depends(get_db),
    gateway: InferenceGateway = Depends(get_inference_gateway),
) -> ChatService:
    return ChatService(db, gateway)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
