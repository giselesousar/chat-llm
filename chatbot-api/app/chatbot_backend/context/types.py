from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict


class ContextMessage(TypedDict):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


@dataclass
class ContextResult:
    messages: list[ContextMessage]
    window_size: int
    includes_system: bool = False
    updated_summary: str | None = field(default=None)
