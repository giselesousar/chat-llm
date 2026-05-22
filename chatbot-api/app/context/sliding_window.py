from __future__ import annotations

from app.context.types import ContextMessage, ContextResult

WINDOW_SIZE = 6


def build_context(messages: list[ContextMessage]) -> list[ContextMessage]:
    return messages[-WINDOW_SIZE:]


class SlidingWindowStrategy:
    def build(
        self,
        messages: list[ContextMessage],
        *,
        system_prompt: str = "",
        conversation_summary: str | None = None,
    ) -> ContextResult:
        selected = build_context(messages)
        return ContextResult(messages=selected, window_size=len(selected))
