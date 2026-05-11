"""Compatível com `uvicorn main:app` com cwd em `chat-llm/backend/` (esta pasta)."""

from app.main import app

__all__ = ["app"]
