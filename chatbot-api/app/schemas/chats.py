from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.openai import ChannelType

MessageRole = Literal["system", "user", "assistant", "tool"]


class ChatSummary(BaseModel):
    chat_id: str = Field(description="UUID público do chat (session_id).")
    channel: ChannelType
    created_at: datetime
    updated_at: datetime
    preview: str | None = Field(default=None, description="Prévia da última mensagem.")


class ChatListResponse(BaseModel):
    items: list[ChatSummary]


class ChatCreateRequest(BaseModel):
    channel: ChannelType = "web"
    chat_id: str | None = Field(default=None, max_length=36, description="UUID opcional.")


class ChatRead(BaseModel):
    chat_id: str
    channel: ChannelType
    created_at: datetime
    updated_at: datetime


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: MessageRole
    content: str
    created_at: datetime


class MessageListResponse(BaseModel):
    chat_id: str
    messages: list[MessageRead]


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    model: str = Field(min_length=1, max_length=128, default="llama3")
    system_prompt: str | None = Field(default=None, max_length=10000)


class SendMessageResponse(BaseModel):
    chat_id: str
    user_message: MessageRead
    assistant_message: MessageRead
    latency_ms: int
    context_window_size: int
    context_strategy: str = Field(
        description="Estratégia de contexto usada nesta requisição.",
    )
