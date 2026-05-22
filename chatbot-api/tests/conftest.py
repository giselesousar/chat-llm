import os
os.environ["DATABASE_URL"] = "sqlite://"

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_chat_service, get_current_user, get_db, get_inference_gateway
from app.services.chat_service import ChatService
from app.clients.inference_gateway import InferenceGateway
from app.core.security import create_access_token, get_password_hash
from app.db import Base
from app.main import app
from app.models.user import User
from app.repositories.user_repository import UserRepository


class FakeLLMProvider:
    def __init__(self, response: dict[str, Any] | None = None) -> None:
        self.last_payload: dict[str, Any] | None = None
        self._response = response or {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 1,
            "model": "test-model",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "resposta mock"},
                    "finish_reason": "stop",
                },
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
        }

    def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.last_payload = payload
        return dict(self._response)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(bind=engine)
    db = session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = UserRepository(db_session).create(
        username="tester",
        hashed_password=get_password_hash("secret123"),
    )
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def fake_llm() -> FakeLLMProvider:
    return FakeLLMProvider()


@pytest.fixture
def client(
    db_session: Session,
    test_user: User,
    fake_llm: FakeLLMProvider,
) -> Generator[TestClient, None, None]:
    def override_db() -> Generator[Session, None, None]:
        yield db_session

    def override_user() -> User:
        return test_user

    def override_gateway() -> InferenceGateway:
        return InferenceGateway(fake_llm)  # type: ignore[arg-type]

    def override_chat_service() -> ChatService:
        return ChatService(db_session, override_gateway())

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_inference_gateway] = override_gateway
    app.dependency_overrides[get_chat_service] = override_chat_service

    token = create_access_token(subject=test_user.username)
    with TestClient(app) as test_client:
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        test_client.fake_llm = fake_llm  # type: ignore[attr-defined]
        test_client.db = db_session  # type: ignore[attr-defined]
        yield test_client

    app.dependency_overrides.clear()
