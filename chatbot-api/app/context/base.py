from __future__ import annotations

from typing import Protocol

from app.context.types import ContextMessage, ContextResult


class ContextStrategy(Protocol):
    def build(
        self,
        messages: list[ContextMessage],
        *,
        system_prompt: str = "",
        conversation_summary: str | None = None,
    ) -> ContextResult: ...
