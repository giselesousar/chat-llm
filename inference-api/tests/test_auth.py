import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_completions_without_key_returns_401(client: TestClient) -> None:
    response = client.post(
        "/v1/chat/completions",
        json={"model": "m", "messages": [{"role": "user", "content": "hi"}], "stream": False},
    )
    assert response.status_code == 401


def test_health_is_public(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
