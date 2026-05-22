from __future__ import annotations

from app.chatbot_backend.context.types import ContextMessage, ContextResult
from app.core.config import CHAT_DEFAULT_SYSTEM_PROMPT

MAX_HISTORY = 4
SYSTEM_PROMPT = CHAT_DEFAULT_SYSTEM_PROMPT


def build_context(
    messages: list[ContextMessage],
    *,
    system_prompt: str | None = None,
) -> list[ContextMessage]:
    prompt = (system_prompt or SYSTEM_PROMPT).strip() or SYSTEM_PROMPT
    history = messages[-MAX_HISTORY:]
    return [
        {"role": "system", "content": prompt},
        *history,
    ]


class FixedSystemStrategy:
    def build(
        self,
        messages: list[ContextMessage],
        *,
        system_prompt: str = "",
        conversation_summary: str | None = None,
    ) -> ContextResult:
        selected = build_context(messages, system_prompt=system_prompt or None)
        history_count = max(0, len(selected) - 1)
        return ContextResult(
            messages=selected,
            window_size=history_count,
            includes_system=True,
        )
