from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.chatbot_backend.services.chat_session_service import ChatSessionService
from app.chatbot_backend.services.context_service import ContextService
from app.chatbot_backend.services.prompt_builder_service import PromptBuilderService
from app.inference_api.gateway import InferenceGateway
from app.models.user import User
from app.repositories.message_repository import MessageRepository
from app.schemas.openai import ChatCompletionMetadata, ChatCompletionRequest, ChatMessage


@dataclass
class OrchestratorResult:
    response: dict[str, Any]
    metadata: ChatCompletionMetadata


class ChatOrchestratorService:
    def __init__(
        self,
        db: Session,
        inference_gateway: InferenceGateway,
    ) -> None:
        self._db = db
        self._gateway = inference_gateway
        self._sessions = ChatSessionService(db)
        self._context = ContextService(db)
        self._prompt_builder = PromptBuilderService()
        self._messages = MessageRepository(db)

    def handle(
        self,
        request: ChatCompletionRequest,
        user: User,
    ) -> OrchestratorResult:
        started = time.perf_counter()

        session = self._sessions.resolve(
            user_id=user.id,
            session_id=request.session_id,
            channel=request.channel,
        )

        context_messages, context_size = self._context.build_context_messages(
            user_id=user.id,
            session_pk=session.id,
        )

        built_messages = self._prompt_builder.build(request, context_messages)

        latest_user = self._latest_user_content(request.messages)
        inference_request = request.model_copy(update={"messages": built_messages})
        llm_response = self._gateway.chat_completion(inference_request)

        assistant_content = self._extract_assistant_content(llm_response)

        if latest_user:
            self._messages.add(
                session_pk=session.id,
                role="user",
                content=latest_user,
            )
        if assistant_content:
            self._messages.add(
                session_pk=session.id,
                role="assistant",
                content=assistant_content,
            )

        self._db.commit()

        latency_ms = int((time.perf_counter() - started) * 1000)
        metadata = ChatCompletionMetadata(
            session_id=session.session_id,
            channel=session.channel,
            latency_ms=latency_ms,
            context_window_size=context_size,
            persisted=True,
        )

        response_body = {**llm_response, "metadata": metadata.model_dump()}
        return OrchestratorResult(response=response_body, metadata=metadata)

    @staticmethod
    def _latest_user_content(messages: list[ChatMessage]) -> str:
        for m in reversed(messages):
            if m.role == "user" and m.content:
                return m.content
        return ""

    @staticmethod
    def _extract_assistant_content(llm_response: dict[str, Any]) -> str:
        choices = llm_response.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""
        first = choices[0]
        if not isinstance(first, dict):
            return ""
        message = first.get("message")
        if not isinstance(message, dict):
            return ""
        content = message.get("content")
        return content if isinstance(content, str) else ""
