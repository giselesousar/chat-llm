from app.chatbot_backend.context.fixed_system import (
    FixedSystemStrategy,
    build_context,
)


def test_build_context_prepends_system_and_limits_history(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.chatbot_backend.context.fixed_system.MAX_HISTORY",
        4,
    )
    messages = [{"role": "user", "content": f"m{i}"} for i in range(8)]
    result = build_context(messages, system_prompt="Instruções para o modelo")
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "Instruções para o modelo"
    assert len(result) == 5
    assert result[1]["content"] == "m4"


def test_strategy_sets_includes_system() -> None:
    messages = [{"role": "user", "content": "olá"}]
    result = FixedSystemStrategy().build(messages, system_prompt="Sys")
    assert result.includes_system is True
    assert result.window_size == 1
