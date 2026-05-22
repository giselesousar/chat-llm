import json
from collections.abc import Generator, Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_completion_service
from app.main import app
from app.services.completion import CompletionService


class FakeLLMProvider:
    def __init__(self, response: dict[str, Any] | None = None) -> None:
        self.last_payload: dict[str, Any] | None = None
        self._response = response or {
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "mock"},
                    "finish_reason": "stop",
                },
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
        }

    def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.last_payload = payload
        return dict(self._response)

    def chat_completions_stream(self, payload: dict[str, Any]) -> Iterator[bytes]:
        self.last_payload = payload
        chunk = {
            "id": "chatcmpl-stream",
            "object": "chat.completion.chunk",
            "choices": [{"index": 0, "delta": {"content": "mock"}, "finish_reason": None}],
        }
        yield f"data: {json.dumps(chunk)}\n\n".encode()
        yield b"data: [DONE]\n\n"


@pytest.fixture
def fake_llm() -> FakeLLMProvider:
    return FakeLLMProvider()


@pytest.fixture
def client(fake_llm: FakeLLMProvider) -> Generator[TestClient, None, None]:
    def override_service() -> CompletionService:
        return CompletionService(fake_llm)

    app.dependency_overrides[get_completion_service] = override_service
    with TestClient(app) as tc:
        tc.headers.update({"X-API-Key": "dev-inference-key"})
        tc.fake_llm = fake_llm  # type: ignore[attr-defined]
        yield tc
    app.dependency_overrides.clear()


def test_completions_with_valid_key(client: TestClient) -> None:
    response = client.post(
        "/v1/chat/completions",
        json={"model": "m", "messages": [{"role": "user", "content": "hi"}], "stream": False},
    )
    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "mock"
