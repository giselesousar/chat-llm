from app.inference_api.bridge import llm_response_to_openai, request_to_llm_payload
from app.schemas.openai import ChatCompletionRequest, ChatMessage


def test_request_to_llm_payload_strips_chatbot_fields() -> None:
    request = ChatCompletionRequest(
        model="m",
        messages=[ChatMessage(role="user", content="hi")],
        session_id="abc",
        channel="web",
    )
    payload = request_to_llm_payload(request)
    assert "session_id" not in payload
    assert "channel" not in payload
    assert payload["model"] == "m"


def test_llm_response_to_openai_normalizes() -> None:
    raw = {
        "choices": [{"message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
    }
    out = llm_response_to_openai(raw, model="m")
    assert out["object"] == "chat.completion"
    assert out["choices"][0]["message"]["content"] == "ok"
