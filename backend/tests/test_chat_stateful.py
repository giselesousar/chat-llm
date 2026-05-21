from sqlalchemy import select

from app.models.chat_message import ChatMessage as ChatMessageModel
from app.models.chat_session import ChatSession


def _chat_payload(**overrides: object) -> dict:
    base = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Olá"}],
        "stream": False,
    }
    base.update(overrides)
    return base


def test_creates_session_when_session_id_absent(client) -> None:
    response = client.post("/v1/chat/completions", json=_chat_payload())
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert data["metadata"]["session_id"]
    assert data["metadata"]["persisted"] is True


def test_reuses_existing_session(client) -> None:
    first = client.post("/v1/chat/completions", json=_chat_payload()).json()
    session_id = first["metadata"]["session_id"]

    second = client.post(
        "/v1/chat/completions",
        json=_chat_payload(session_id=session_id, messages=[{"role": "user", "content": "Segunda"}]),
    )
    assert second.status_code == 200
    assert second.json()["metadata"]["session_id"] == session_id

    sessions = client.db.scalars(select(ChatSession)).all()
    assert len(sessions) == 1


def test_rejects_payload_over_message_limit(client) -> None:
    messages = [{"role": "user", "content": f"m{i}"} for i in range(60)]
    response = client.post("/v1/chat/completions", json=_chat_payload(messages=messages))
    assert response.status_code == 422


def test_includes_context_in_llm_call(client) -> None:
    first = client.post("/v1/chat/completions", json=_chat_payload()).json()
    session_id = first["metadata"]["session_id"]

    client.post(
        "/v1/chat/completions",
        json=_chat_payload(
            session_id=session_id,
            messages=[{"role": "user", "content": "Com contexto"}],
        ),
    )

    assert client.fake_llm.last_payload is not None
    roles = [m["role"] for m in client.fake_llm.last_payload["messages"]]
    assert "user" in roles


def test_persists_user_and_assistant_messages(client) -> None:
    client.post("/v1/chat/completions", json=_chat_payload())
    rows = client.db.scalars(select(ChatMessageModel)).all()
    roles = {r.role for r in rows}
    assert "user" in roles
    assert "assistant" in roles


def test_returns_structured_metadata(client) -> None:
    response = client.post(
        "/v1/chat/completions",
        json=_chat_payload(channel="cli"),
    )
    meta = response.json()["metadata"]
    assert meta["channel"] == "cli"
    assert isinstance(meta["latency_ms"], int)
    assert isinstance(meta["context_window_size"], int)
    assert "choices" in response.json()


def test_channel_does_not_break_contract(client) -> None:
    for channel in ("web", "cli", "app"):
        response = client.post(
            "/v1/chat/completions",
            json=_chat_payload(channel=channel),
        )
        assert response.status_code == 200
        assert response.json()["metadata"]["channel"] == channel


def test_orchestrator_uses_llm_port_not_http_adapter() -> None:
    import inspect

    from app.chatbot_backend.services.chat_orchestrator_service import ChatOrchestratorService

    source = inspect.getsource(ChatOrchestratorService)
    assert "httpx" not in source
    assert "HttpLLMAdapter" not in source
