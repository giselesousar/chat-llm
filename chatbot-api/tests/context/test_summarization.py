from app.chatbot_backend.context.summarization import (
    SummarizationStrategy,
    build_context,
    summarize,
)


def _messages(n: int) -> list[dict[str, str]]:
    return [{"role": "user", "content": f"msg-{i}"} for i in range(n)]


def test_summarize_joins_first_four_contents() -> None:
    messages = _messages(6)
    summary = summarize(messages)
    assert summary.startswith("Resumo: ")
    assert "msg-0" in summary
    assert "msg-3" in summary


def test_build_context_with_many_messages_adds_summary_system(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.chatbot_backend.context.summarization.SUMMARY_THRESHOLD",
        10,
    )
    monkeypatch.setattr(
        "app.chatbot_backend.context.summarization.MAX_RECENT",
        4,
    )
    messages = _messages(11)
    context, updated = build_context(messages)
    assert updated is not None
    assert context[0]["role"] == "system"
    assert "Resumo da conversa anterior" in context[0]["content"]
    assert len([m for m in context if m["role"] != "system"]) == 4


def test_strategy_persists_updated_summary() -> None:
    messages = _messages(11)
    result = SummarizationStrategy().build(messages)
    assert result.updated_summary is not None
    assert result.includes_system is True
