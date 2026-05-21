from sqlalchemy.orm import Session

from app.core.config import CHAT_MAX_CONTEXT_MESSAGES
from app.repositories.memory_repository import MemoryRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.openai import ChatMessage


class ContextService:
    def __init__(self, db: Session) -> None:
        self._messages = MessageRepository(db)
        self._memory = MemoryRepository(db)

    def build_context_messages(
        self,
        *,
        user_id: int,
        session_pk: int,
    ) -> tuple[list[ChatMessage], int]:
        history = self._messages.list_recent_for_session(
            session_pk,
            limit=CHAT_MAX_CONTEXT_MESSAGES,
        )
        history_messages = [
            ChatMessage(role=m.role, content=m.content) for m in history
        ]

        memory = self._memory.get_by_user_id(user_id)
        if memory is not None and memory.summary.strip():
            memory_msg = ChatMessage(
                role="system",
                content=f"Memória do usuário: {memory.summary}",
            )
            history_messages = [memory_msg, *history_messages]

        return history_messages, len(history_messages)
