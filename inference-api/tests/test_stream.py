from fastapi.testclient import TestClient


def test_stream_returns_sse(client: TestClient) -> None:
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "m",
            "messages": [{"role": "user", "content": "hi"}],
            "stream": True,
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert b"data:" in response.content
    assert client.fake_llm.last_payload is not None
    assert client.fake_llm.last_payload.get("stream") is True


def test_request_payload_includes_stream_flag() -> None:
    from app.schemas.openai import ChatCompletionRequest, ChatMessage
    from app.services.bridge import request_to_llm_payload

    request = ChatCompletionRequest(
        model="m",
        messages=[ChatMessage(role="user", content="hi")],
        stream=True,
    )
    payload = request_to_llm_payload(request)
    assert payload["stream"] is True
