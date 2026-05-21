from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.chatbot_backend.services.chat_orchestrator_service import ChatOrchestratorService
from app.core.security import get_current_user
from app.db import get_db
from app.inference_api.gateway import InferenceGateway
from app.inference_api.http_adapter import HttpLLMAdapter
from app.inference_api.port import LLMProvider
from app.models.user import User
from app.services.user_service import UserService


def get_llm_provider() -> LLMProvider:
    return HttpLLMAdapter()


def get_inference_gateway(
    provider: LLMProvider = Depends(get_llm_provider),
) -> InferenceGateway:
    return InferenceGateway(provider)


def get_chat_orchestrator(
    db: Session = Depends(get_db),
    gateway: InferenceGateway = Depends(get_inference_gateway),
) -> ChatOrchestratorService:
    return ChatOrchestratorService(db, gateway)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


LLMProviderDep = Annotated[LLMProvider, Depends(get_llm_provider)]
InferenceGatewayDep = Annotated[InferenceGateway, Depends(get_inference_gateway)]
ChatOrchestratorDep = Annotated[ChatOrchestratorService, Depends(get_chat_orchestrator)]
DBSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
