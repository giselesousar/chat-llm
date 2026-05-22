from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx

from app.core.config import LLM_BASE_URL, LLM_TIMEOUT_SECONDS
from app.core.exceptions import LLMConnectionError, LLMHTTPError, LLMParseError


class OllamaClient:
    """Cliente HTTP para o endpoint de chat completions do Ollama (ou compatível)."""

    CHAT_COMPLETIONS_PATH = "/v1/chat/completions"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self._base_url = (base_url or LLM_BASE_URL).rstrip("/")
        self._timeout = float(
            timeout_seconds if timeout_seconds is not None else LLM_TIMEOUT_SECONDS,
        )

    def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("stream"):
            msg = "Use chat_completions_stream quando stream=true."
            raise ValueError(msg)
        return self._post_json(self.CHAT_COMPLETIONS_PATH, payload)

    def chat_completions_stream(self, payload: dict[str, Any]) -> Iterator[bytes]:
        body = {**payload, "stream": True}
        url = f"{self._base_url}{self.CHAT_COMPLETIONS_PATH}"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                with client.stream("POST", url, json=body) as response:
                    if response.status_code >= 400:
                        text = (response.read() or response.reason_phrase or b"").decode(
                            errors="replace",
                        )
                        raise LLMHTTPError(response.status_code, text.strip())
                    yield from response.iter_bytes()
        except httpx.RequestError as exc:
            raise LLMConnectionError(
                f"Não foi possível contactar Ollama em {self._base_url}: {exc!s}",
            ) from exc

    def _post_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=body)
        except httpx.RequestError as exc:
            raise LLMConnectionError(
                f"Não foi possível contactar Ollama em {self._base_url}: {exc!s}",
            ) from exc

        if response.status_code >= 400:
            text = (response.text or response.reason_phrase or "").strip()
            raise LLMHTTPError(response.status_code, text)

        return self._parse_json_object(response)

    def _parse_json_object(self, response: httpx.Response) -> dict[str, Any]:
        text = response.text
        if not text.strip():
            raise LLMParseError("Resposta vazia do servidor LLM")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            preview = text[:500]
            raise LLMParseError(f"JSON inválido (prévia): {preview}") from exc

        if not isinstance(data, dict):
            raise LLMParseError("JSON do servidor LLM não é um objeto na raiz")
        return data
