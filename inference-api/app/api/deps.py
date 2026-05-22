from app.adapters.ollama import OllamaClient
from app.services.completion import CompletionService


def get_completion_service() -> CompletionService:
    return CompletionService(OllamaClient())
