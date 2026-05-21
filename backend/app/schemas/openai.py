from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.config import (
    CHAT_MAX_CONTENT_CHARS,
    CHAT_MAX_MESSAGES,
)

ChannelType = Literal["web", "cli", "app"]


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: str = Field(min_length=1, max_length=32)
    content: str | None = None

    @field_validator("content")
    @classmethod
    def validate_content_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > CHAT_MAX_CONTENT_CHARS:
            msg = f"content excede {CHAT_MAX_CONTENT_CHARS} caracteres"
            raise ValueError(msg)
        return v


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str = Field(min_length=1, max_length=128)
    messages: list[ChatMessage] = Field(min_length=1)
    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(default=None, ge=0, le=1)
    max_tokens: int | None = Field(default=None, ge=1, le=128_000)
    stop: str | list[str] | None = None
    stream: bool = False
    session_id: str | None = Field(default=None, max_length=36)
    channel: ChannelType = "web"

    @field_validator("messages")
    @classmethod
    def validate_messages_count(cls, v: list[ChatMessage]) -> list[ChatMessage]:
        if len(v) > CHAT_MAX_MESSAGES:
            msg = f"messages excede o limite de {CHAT_MAX_MESSAGES}"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_has_user_message(self) -> "ChatCompletionRequest":
        if not any(m.role == "user" for m in self.messages):
            msg = "pelo menos uma mensagem com role=user é obrigatória"
            raise ValueError(msg)
        return self


class ChatCompletionMetadata(BaseModel):
    session_id: str
    channel: str
    latency_ms: int
    context_window_size: int
    persisted: bool


class ChatCompletionResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    object: str
    created: int
    model: str
    choices: list[dict]
    usage: dict
    metadata: ChatCompletionMetadata
