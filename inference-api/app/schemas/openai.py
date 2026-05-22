from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_MESSAGES = 50
MAX_CONTENT_CHARS = 10_000

# Papéis aceitos no contrato OpenAI-like (Chat Completions API).
MessageRole = Literal["system", "user", "assistant", "tool"]

# Motivos de término de geração retornados pelo provedor de inferência.
FinishReason = Literal[
    "stop",
    "length",
    "tool_calls",
    "content_filter",
    "function_call",
]


class ChatMessage(BaseModel):
    """Uma mensagem no histórico do chat."""

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {"role": "user", "content": "Olá, como você pode me ajudar?"},
                {"role": "system", "content": "Você é um assistente útil."},
            ]
        },
    )

    role: MessageRole = Field(
        description=(
            "Papel da mensagem no diálogo. Valores suportados: "
            "`system` (instruções globais), `user` (entrada do usuário), "
            "`assistant` (resposta do modelo), `tool` (resultado de ferramenta). "
            "É obrigatório incluir ao menos uma mensagem com `role=user`."
        ),
        json_schema_extra={"enum": ["system", "user", "assistant", "tool"]},
    )
    content: str | None = Field(
        default=None,
        description="Texto da mensagem. Pode ser omitido ou null em fluxos com ferramentas.",
        max_length=MAX_CONTENT_CHARS,
    )

    @field_validator("content")
    @classmethod
    def validate_content_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > MAX_CONTENT_CHARS:
            msg = f"content excede {MAX_CONTENT_CHARS} caracteres"
            raise ValueError(msg)
        return v


class ChatCompletionRequest(BaseModel):
    """Corpo da requisição `POST /v1/chat/completions` (compatível com OpenAI)."""

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {
                    "model": "llama3",
                    "messages": [
                        {"role": "system", "content": "Você é um assistente útil."},
                        {"role": "user", "content": "Explique o que é um LLM em uma frase."},
                    ],
                    "temperature": 0.7,
                    "stream": False,
                }
            ]
        },
    )

    model: str = Field(
        min_length=1,
        max_length=128,
        description="Identificador do modelo no servidor de inferência (ex.: nome do modelo Ollama).",
        examples=["llama3", "qwen2.5"],
    )
    messages: list[ChatMessage] = Field(
        min_length=1,
        description="Histórico de mensagens. Deve conter pelo menos uma com `role=user`.",
    )
    temperature: float | None = Field(
        default=None,
        ge=0,
        le=2,
        description="Amostragem: 0 = determinístico, valores maiores = mais variável.",
    )
    top_p: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Nucleus sampling (top-p). Alternativa ou complemento a `temperature`.",
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        le=128_000,
        description="Limite máximo de tokens na resposta do assistente.",
    )
    stop: str | list[str] | None = Field(
        default=None,
        description="Sequência(s) que interrompem a geração quando encontradas.",
    )
    stream: bool = Field(
        default=False,
        description="Se `true`, resposta em SSE (`text/event-stream`, formato OpenAI).",
    )

    @field_validator("messages")
    @classmethod
    def validate_messages_count(cls, v: list[ChatMessage]) -> list[ChatMessage]:
        if len(v) > MAX_MESSAGES:
            msg = f"messages excede o limite de {MAX_MESSAGES}"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_has_user_message(self) -> "ChatCompletionRequest":
        if not any(m.role == "user" for m in self.messages):
            msg = "pelo menos uma mensagem com role=user é obrigatória"
            raise ValueError(msg)
        return self


class ChoiceMessage(BaseModel):
    """Mensagem retornada em uma opção de completion."""

    model_config = ConfigDict(extra="allow")

    role: MessageRole = Field(
        description="Papel da mensagem gerada (em geral `assistant`).",
    )
    content: str = Field(
        default="",
        description="Texto gerado pelo modelo.",
    )


class ChatChoice(BaseModel):
    """Uma opção de resposta na lista `choices`."""

    model_config = ConfigDict(extra="allow")

    index: int = Field(description="Índice da opção (geralmente 0).")
    message: ChoiceMessage
    finish_reason: FinishReason | None = Field(
        default=None,
        description="Motivo pelo qual a geração terminou.",
    )


class UsageInfo(BaseModel):
    """Contagem de tokens consumidos na requisição."""

    model_config = ConfigDict(extra="allow")

    prompt_tokens: int = Field(ge=0, description="Tokens no prompt enviado.")
    completion_tokens: int = Field(ge=0, description="Tokens na resposta gerada.")
    total_tokens: int = Field(ge=0, description="Soma de prompt + completion.")


class ChatCompletionResponse(BaseModel):
    """Resposta no formato OpenAI Chat Completions."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(description="Identificador único da completion.")
    object: Literal["chat.completion"] = Field(
        default="chat.completion",
        description="Tipo do objeto (sempre `chat.completion`).",
    )
    created: int = Field(description="Unix timestamp (segundos) de criação da resposta.")
    model: str = Field(description="Modelo usado na inferência.")
    choices: list[ChatChoice] = Field(description="Lista de completions.")
    usage: UsageInfo
