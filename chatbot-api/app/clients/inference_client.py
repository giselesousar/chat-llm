from __future__ import annotations

import json
from typing import Any

import httpx

from app.clients.exceptions import (
    InferenceConnectionError,
    InferenceHTTPError,
    InferenceParseError,
)
from app.core.config import INFERENCE_API_KEY, INFERENCE_BASE_URL

INFERENCE_TIMEOUT_SECONDS = 120.0


class InferenceHttpClient:
    """Cliente HTTP para a inference-api (implementa o contrato LLMProvider)."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float = INFERENCE_TIMEOUT_SECONDS,
    ) -> None:
        self._base_url = (base_url or INFERENCE_BASE_URL).rstrip("/")
        self._api_key = api_key or INFERENCE_API_KEY
        self._timeout = timeout_seconds

    def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}/v1/chat/completions"
        headers = {"X-API-Key": self._api_key}
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=payload, headers=headers)
        except httpx.RequestError as exc:
            raise InferenceConnectionError(
                f"Não foi possível contactar inference-api em {self._base_url}: {exc!s}",
            ) from exc

        if response.status_code == 401:
            raise InferenceHTTPError(
                401,
                "Falha de autenticação com inference-api (verifique INFERENCE_API_KEY)",
            )
        if response.status_code >= 400:
            text = (response.text or response.reason_phrase or "").strip()
            raise InferenceHTTPError(response.status_code, text)

        return self._parse_json_object(response)

    def _parse_json_object(self, response: httpx.Response) -> dict[str, Any]:
        text = response.text
        if not text.strip():
            raise InferenceParseError("Resposta vazia da inference-api")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise InferenceParseError(f"JSON inválido: {text[:500]}") from exc
        if not isinstance(data, dict):
            raise InferenceParseError("JSON da inference-api não é um objeto")
        return data
