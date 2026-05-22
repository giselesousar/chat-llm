from app.chatbot_backend.context.sliding_window import (
    SlidingWindowStrategy,
    build_context,
)


def _messages(n: int) -> list[dict[str, str]]:
    return [{"role": "user", "content": f"msg-{i}"} for i in range(n)]


def test_build_context_returns_last_six() -> None:
    messages = _messages(10)
    result = build_context(messages)
    assert len(result) == 6
    assert result[0]["content"] == "msg-4"
    assert result[-1]["content"] == "msg-9"


def test_strategy_window_size() -> None:
    result = SlidingWindowStrategy().build(_messages(10))
    assert result.window_size == 6
    assert result.includes_system is False
