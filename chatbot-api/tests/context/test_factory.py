import pytest

from app.context.factory import get_context_strategy
from app.context.fixed_system import FixedSystemStrategy
from app.context.sliding_window import SlidingWindowStrategy
from app.context.summarization import SummarizationStrategy
from app.context.token_limit import TokenLimitStrategy


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
