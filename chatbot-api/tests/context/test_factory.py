import pytest

from app.chatbot_backend.context.factory import get_context_strategy
from app.chatbot_backend.context.fixed_system import FixedSystemStrategy
from app.chatbot_backend.context.sliding_window import SlidingWindowStrategy
from app.chatbot_backend.context.summarization import SummarizationStrategy
from app.chatbot_backend.context.token_limit import TokenLimitStrategy


@pytest.mark.parametrize(
    ("strategy_name", "expected_cls"),
    [
        ("sliding_window", SlidingWindowStrategy),
        ("token_limit", TokenLimitStrategy),
        ("fixed_system", FixedSystemStrategy),
        ("summarization", SummarizationStrategy),
    ],
)
def test_get_context_strategy_by_name(strategy_name: str, expected_cls: type) -> None:
    strategy = get_context_strategy(strategy_name)
    assert isinstance(strategy, expected_cls)


def test_invalid_strategy_raises() -> None:
    with pytest.raises(ValueError, match="CONTEXT_STRATEGY inválida"):
        get_context_strategy("invalid")
