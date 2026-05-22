from __future__ import annotations

from app.chatbot_backend.context.types import ContextMessage, ContextResult

MAX_TOKENS = 100


def count_tokens(text: str) -> int:
    # Proxy didático: em produção use o tokenizer do modelo (ex.: tiktoken).
    return len(text.split())


def build_context(messages: list[ContextMessage]) -> list[ContextMessage]:
    selected: list[ContextMessage] = []
    current_tokens = 0

    for msg in reversed(messages):
        tokens = count_tokens(msg["content"])

        if current_tokens + tokens > MAX_TOKENS:
            break

        selected.insert(0, msg)
        current_tokens += tokens

    return selected


class TokenLimitStrategy:
    def build(
        self,
        messages: list[ContextMessage],
        *,
        system_prompt: str = "",
        conversation_summary: str | None = None,
    ) -> ContextResult:
        selected = build_context(messages)
        return ContextResult(messages=selected, window_size=len(selected))
