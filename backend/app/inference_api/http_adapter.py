from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import LLM_BASE_URL, LLM_TIMEOUT_SECONDS
from app.inference_api.exceptions import LLMConnectionError, LLMHTTPError, LLMParseError


class HttpLLMAdapter:
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
        return self._post_json(self.CHAT_COMPLETIONS_PATH, payload)

    def _post_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=body)
        except httpx.RequestError as exc:
            raise LLMConnectionError(
                f"Não foi possível contatar o servidor de inferência em {self._base_url}: {exc!s}",
            ) from exc

        if response.status_code >= 400:
            text = (response.text or response.reason_phrase or "").strip()
            raise LLMHTTPError(response.status_code, text)

        return self._parse_json_object(response)

    def _parse_json_object(self, response: httpx.Response) -> dict[str, Any]:
        text = response.text
        if not text.strip():
            raise LLMParseError("Resposta vazia do servidor de inferência")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            preview = text[:500]
            raise LLMParseError(f"JSON inválido (prévia): {preview}") from exc

        if not isinstance(data, dict):
            raise LLMParseError("JSON do servidor de inferência não é um objeto na raiz")
        return data
