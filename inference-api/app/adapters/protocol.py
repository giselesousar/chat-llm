from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Protocol


class LLMProvider(Protocol):
    def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        pass

    def chat_completions_stream(self, payload: dict[str, Any]) -> Iterator[bytes]:
        pass
