from app.inference_api import (
    HttpLLMAdapter,
    InferenceGateway,
    LLMConnectionError,
    LLMHTTPError,
    LLMParseError,
    LLMProvider,
    LLMProviderError,
)
from app.inference_api.bridge import llm_response_to_openai, request_to_llm_payload

OllamaProvider = HttpLLMAdapter
OllamaConnectionError = LLMConnectionError
OllamaHTTPError = LLMHTTPError
OllamaParseError = LLMParseError
OllamaProviderError = LLMProviderError
openai_chat_completion_request_to_ollama_payload = request_to_llm_payload
ollama_to_openai = llm_response_to_openai

__all__ = [
    "HttpLLMAdapter",
    "InferenceGateway",
    "LLMConnectionError",
    "LLMHTTPError",
    "LLMParseError",
    "LLMProvider",
    "LLMProviderError",
    "OllamaConnectionError",
    "OllamaHTTPError",
    "OllamaParseError",
    "OllamaProvider",
    "OllamaProviderError",
    "llm_response_to_openai",
    "ollama_to_openai",
    "openai_chat_completion_request_to_ollama_payload",
    "request_to_llm_payload",
]
