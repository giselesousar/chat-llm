from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import CHAT_DEFAULT_SYSTEM_PROMPT, CHAT_MAX_CONTEXT_MESSAGES
from app.chatbot_backend.inference_gateway import InferenceGateway
from app.models.chat_session import ChatSession
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.schemas.openai import ChatCompletionMetadata, ChatCompletionRequest, ChatMessage


@dataclass
class ChatResult:
    response: dict[str, Any]
    metadata: ChatCompletionMetadata


class ChatService:
    """Pipeline do chatbot: sessão → contexto → prompt → inferência → persistência."""

    def __init__(
        self,
        db: Session,
        inference_gateway: InferenceGateway,
    ) -> None:
        self._db = db
        self._gateway = inference_gateway
        self._repo = ChatRepository(db)

    def handle(
        self,
        request: ChatCompletionRequest,
        user: User,
    ) -> ChatResult:
        started = time.perf_counter()

        session = self._resolve_session(
            user_id=user.id,
            session_id=request.session_id,
            channel=request.channel,
        )

        context_messages, context_size = self._build_context(session_pk=session.id)
        built_messages = self._build_prompt(request, context_messages)

        latest_user = self._latest_user_content(request.messages)
        inference_request = request.model_copy(update={"messages": built_messages})
        llm_response = self._gateway.chat_completion(inference_request)

        assistant_content = self._extract_assistant_content(llm_response)

        if latest_user:
            self._repo.add_message(
                session_pk=session.id,
                role="user",
                content=latest_user,
            )
        if assistant_content:
            self._repo.add_message(
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
        return ChatResult(response=response_body, metadata=metadata)

    def _resolve_session(
        self,
        *,
        user_id: int,
        session_id: str | None,
        channel: str,
    ) -> ChatSession:
        if session_id:
            existing = self._repo.get_session_by_public_id(session_id, user_id=user_id)
            if existing is not None:
                return existing
            from app.core.exceptions import ChatNotFoundError

            raise ChatNotFoundError(session_id)
        public_id = str(uuid.uuid4())
        return self._repo.create_session(
            session_id=public_id,
            user_id=user_id,
            channel=channel,
        )

    def _build_context(self, *, session_pk: int) -> tuple[list[ChatMessage], int]:
        history = self._repo.list_recent_messages(
            session_pk,
            limit=CHAT_MAX_CONTEXT_MESSAGES,
        )
        history_messages = [
            ChatMessage(role=m.role, content=m.content) for m in history
        ]
        return history_messages, len(history_messages)

    def _build_prompt(
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


    def list_chats(self, user: User) -> list[ChatSession]:
        return self._repo.list_sessions_by_user(user.id)

    def create_chat(
        self,
        user: User,
        *,
        channel: str = "web",
        chat_id: str | None = None,
    ) -> ChatSession:
        public_id = chat_id or str(uuid.uuid4())
        if chat_id:
            existing = self._repo.get_session_by_public_id(chat_id, user_id=user.id)
            if existing is not None:
                return existing
        return self._repo.create_session(
            session_id=public_id,
            user_id=user.id,
            channel=channel,
        )

    def get_chat(self, chat_id: str, user: User) -> ChatSession:
        session = self._repo.get_session_by_public_id(chat_id, user_id=user.id)
        if session is None:
            from app.core.exceptions import ChatNotFoundError

            raise ChatNotFoundError(chat_id)
        return session

    def delete_chat(self, chat_id: str, user: User) -> None:
        session = self.get_chat(chat_id, user)
        self._repo.delete_session(session)
        self._db.commit()

    def list_messages(self, chat_id: str, user: User) -> tuple[ChatSession, list]:
        session = self.get_chat(chat_id, user)
        messages = self._repo.list_messages(session.id)
        return session, messages

