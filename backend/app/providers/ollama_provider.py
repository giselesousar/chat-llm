from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import OLLAMA_BASE_URL, OLLAMA_TIMEOUT_SECONDS
from app.providers.ollama_exceptions import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaParseError,
)


class OllamaProvider:
    CHAT_COMPLETIONS_PATH = "/v1/chat/completions"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self._base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")
        self._timeout = float(timeout_seconds if timeout_seconds is not None else OLLAMA_TIMEOUT_SECONDS)

    def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_json(self.CHAT_COMPLETIONS_PATH, payload)

    def _post_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=body)
        except httpx.RequestError as exc:
            raise OllamaConnectionError(
                f"Não foi possível contatar o Ollama em {self._base_url}: {exc!s}",
            ) from exc

        if response.status_code >= 400:
            text = (response.text or response.reason_phrase or "").strip()
            raise OllamaHTTPError(response.status_code, text)

        return self._parse_json_object(response)

    def _parse_json_object(self, response: httpx.Response) -> dict[str, Any]:
        text = response.text
        if not text.strip():
            raise OllamaParseError("Resposta vazia do Ollama")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            preview = text[:500]
            raise OllamaParseError(f"JSON inválido (prévia): {preview}") from exc

        if not isinstance(data, dict):
            raise OllamaParseError("JSON do Ollama não é um objeto na raiz")
        return data
