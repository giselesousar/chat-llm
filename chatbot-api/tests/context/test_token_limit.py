from app.context.token_limit import (
    TokenLimitStrategy,
    build_context,
    count_tokens,
)


def test_count_tokens_splits_on_whitespace() -> None:
    assert count_tokens("one two three") == 3


def test_build_context_stops_before_exceeding_max_tokens(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.context.token_limit.MAX_TOKENS",
        9,
    )
    messages = [
        {"role": "user", "content": "one two three four five"},
        {"role": "assistant", "content": "six seven eight"},
        {"role": "user", "content": "nine ten"},
    ]
    result = build_context(messages)
    assert len(result) == 2
    assert result[-1]["content"] == "nine ten"


def test_strategy_returns_selected_count() -> None:
    messages = [{"role": "user", "content": "a b c d e f g h i j"}]
    result = TokenLimitStrategy().build(messages)
    assert result.window_size == len(result.messages)
