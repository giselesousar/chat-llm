from sqlalchemy import select

from app.models.chat_message import ChatMessage as ChatMessageModel
from app.models.chat_session import ChatSession


def _create_chat(client, *, channel: str = "web") -> str:
    response = client.post("/chats", json={"channel": channel})
    assert response.status_code == 201
    return response.json()["chat_id"]


def _send_message(client, chat_id: str, content: str) -> dict:
    response = client.post(
        f"/chats/{chat_id}/messages",
        json={"content": content, "model": "test-model"},
    )
    assert response.status_code == 200
    return response.json()


def test_creates_chat_on_first_message(client) -> None:
    chat_id = _create_chat(client)
    body = _send_message(client, chat_id, "Olá")
    assert body["chat_id"] == chat_id
    assert body["user_message"]["content"] == "Olá"
    assert body["assistant_message"]["content"] == "resposta mock"


def test_reuses_existing_chat(client) -> None:
    chat_id = _create_chat(client)
    _send_message(client, chat_id, "Primeira")
    second = _send_message(client, chat_id, "Segunda")
    assert second["chat_id"] == chat_id

    sessions = client.db.scalars(select(ChatSession)).all()
    assert len(sessions) == 1


def test_includes_context_in_llm_call(client) -> None:
    chat_id = _create_chat(client)
    _send_message(client, chat_id, "Primeira")
    client.fake_llm.last_payload = None
    _send_message(client, chat_id, "Com contexto")

    assert client.fake_llm.last_payload is not None
    roles = [m["role"] for m in client.fake_llm.last_payload["messages"]]
    assert "user" in roles


def test_persists_user_and_assistant_messages(client) -> None:
    chat_id = _create_chat(client)
    _send_message(client, chat_id, "Olá")
    rows = client.db.scalars(select(ChatMessageModel)).all()
    roles = {r.role for r in rows}
    assert "user" in roles
    assert "assistant" in roles


def test_returns_latency_and_context_size(client) -> None:
    chat_id = _create_chat(client, channel="cli")
    body = _send_message(client, chat_id, "Olá")
    assert isinstance(body["latency_ms"], int)
    assert isinstance(body["context_window_size"], int)

    session = client.db.scalars(select(ChatSession)).first()
    assert session is not None
    assert session.channel == "cli"


def test_channel_on_create(client) -> None:
    for channel in ("web", "cli", "app"):
        chat_id = _create_chat(client, channel=channel)
        session = client.db.scalars(
            select(ChatSession).where(ChatSession.session_id == chat_id),
        ).first()
        assert session is not None
        assert session.channel == channel


def test_chat_service_uses_inference_client_not_httpx_directly() -> None:
    import inspect

    from app.chatbot_backend.chat_service import ChatService

    source = inspect.getsource(ChatService)
    assert "httpx" not in source
    assert "InferenceHttpClient" not in source
