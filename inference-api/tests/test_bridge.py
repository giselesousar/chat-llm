from app.services.bridge import llm_response_to_openai, request_to_llm_payload
from app.schemas.openai import ChatCompletionRequest, ChatMessage


def test_request_to_llm_payload_pure() -> None:
    request = ChatCompletionRequest(
        model="m",
        messages=[ChatMessage(role="user", content="hi")],
    )
    payload = request_to_llm_payload(request)
    assert payload["model"] == "m"
    assert "session_id" not in payload


def test_llm_response_to_openai_normalizes() -> None:
    raw = {
        "choices": [{"message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
    }
    out = llm_response_to_openai(raw, model="m")
    assert out["object"] == "chat.completion"
    assert out["choices"][0]["message"]["content"] == "ok"
