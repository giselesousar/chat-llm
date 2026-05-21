from __future__ import annotations

from typing import Any

from app.inference_api.bridge import llm_response_to_openai, request_to_llm_payload
from app.inference_api.port import LLMProvider
from app.schemas.openai import ChatCompletionRequest


class InferenceGateway:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def chat_completion(self, request: ChatCompletionRequest) -> dict[str, Any]:
        payload = request_to_llm_payload(request)
        raw = self._provider.chat_completions(payload)
        return llm_response_to_openai(raw, model=request.model)
