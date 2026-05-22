from __future__ import annotations

from app.context.base import ContextStrategy
from app.context.fixed_system import FixedSystemStrategy
from app.context.settings import CONTEXT_STRATEGY
from app.context.sliding_window import SlidingWindowStrategy
from app.context.summarization import SummarizationStrategy
from app.context.token_limit import TokenLimitStrategy

_STRATEGIES: dict[str, type[ContextStrategy]] = {
    "sliding_window": SlidingWindowStrategy,
    "token_limit": TokenLimitStrategy,
    "fixed_system": FixedSystemStrategy,
    "summarization": SummarizationStrategy,
}


def get_active_context_strategy_name() -> str:
    return CONTEXT_STRATEGY.strip().lower()


def get_context_strategy(name: str | None = None) -> ContextStrategy:
    key = (name or get_active_context_strategy_name()).strip().lower()
    cls = _STRATEGIES.get(key)
    if cls is None:
        valid = ", ".join(sorted(_STRATEGIES))
        msg = f"CONTEXT_STRATEGY inválida: {key!r}. Valores: {valid}"
        raise ValueError(msg)
    return cls()


def list_context_strategies() -> list[str]:
    return sorted(_STRATEGIES)
