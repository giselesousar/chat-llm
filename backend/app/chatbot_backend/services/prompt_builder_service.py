from app.core.config import CHAT_DEFAULT_SYSTEM_PROMPT
from app.schemas.openai import ChatCompletionRequest, ChatMessage


class PromptBuilderService:
    def build(
        self,
        request: ChatCompletionRequest,
        context_messages: list[ChatMessage],
    ) -> list[ChatMessage]:
        system_from_request = [m for m in request.messages if m.role == "system"]
        latest_user = self._extract_latest_user_message(request.messages)

        merged: list[ChatMessage] = []
        if system_from_request:
            merged.extend(system_from_request)
        elif CHAT_DEFAULT_SYSTEM_PROMPT.strip():
            merged.append(ChatMessage(role="system", content=CHAT_DEFAULT_SYSTEM_PROMPT))

        merged.extend(context_messages)

        other_roles = [
            m
            for m in request.messages
            if m.role not in ("system", "user") and m is not latest_user
        ]
        merged.extend(other_roles)

        if latest_user is not None:
            merged.append(latest_user)

        return merged

    @staticmethod
    def _extract_latest_user_message(
        messages: list[ChatMessage],
    ) -> ChatMessage | None:
        for m in reversed(messages):
            if m.role == "user":
                return m
        return None
