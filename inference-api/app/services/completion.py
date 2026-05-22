from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from app.adapters.protocol import LLMProvider
from app.schemas.openai import ChatCompletionRequest
from app.services.bridge import llm_response_to_openai, request_to_llm_payload


class CompletionService:
    """Orquestra conversão OpenAI-like e chamada ao provedor LLM (Ollama)."""

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    def create(self, request: ChatCompletionRequest) -> dict[str, Any]:
        payload = request_to_llm_payload(request)
        raw = self._llm.chat_completions(payload)
        return llm_response_to_openai(raw, model=request.model)

    def stream(self, request: ChatCompletionRequest) -> Iterator[bytes]:
        payload = request_to_llm_payload(request)
        yield from self._llm.chat_completions_stream(payload)
