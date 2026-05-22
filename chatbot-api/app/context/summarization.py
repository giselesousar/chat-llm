from __future__ import annotations

from app.context.types import ContextMessage, ContextResult

MAX_RECENT = 4
SUMMARY_THRESHOLD = 10


def summarize(messages: list[ContextMessage]) -> str:
    texts = [m["content"] for m in messages]
    return "Resumo: " + " | ".join(texts[:4])


def build_context(
    messages: list[ContextMessage],
    *,
    conversation_summary: str | None = None,
) -> tuple[list[ContextMessage], str | None]:
    summary = conversation_summary
    updated_summary: str | None = None

    if len(messages) > SUMMARY_THRESHOLD:
        old_messages = messages[:-MAX_RECENT]
        summary = summarize(old_messages)
        updated_summary = summary
        recent_messages = messages[-MAX_RECENT:]
    else:
        recent_messages = messages

    context: list[ContextMessage] = []

    if summary:
        context.append(
            {
                "role": "system",
                "content": f"""
Resumo da conversa anterior:
{summary}
""".strip(),
            },
        )

    context.extend(recent_messages)
    return context, updated_summary


class SummarizationStrategy:
    def build(
        self,
        messages: list[ContextMessage],
        *,
        system_prompt: str = "",
        conversation_summary: str | None = None,
    ) -> ContextResult:
        selected, updated_summary = build_context(
            messages,
            conversation_summary=conversation_summary,
        )
        history_count = len([m for m in selected if m["role"] != "system"])
        return ContextResult(
            messages=selected,
            window_size=history_count,
            includes_system=any(m["role"] == "system" for m in selected),
            updated_summary=updated_summary,
        )
