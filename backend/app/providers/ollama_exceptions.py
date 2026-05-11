class OllamaProviderError(Exception):
    """Erro base ao falar com o Ollama."""


class OllamaConnectionError(OllamaProviderError):
    """Falha de rede / timeout antes de resposta HTTP."""


class OllamaHTTPError(OllamaProviderError):
    """Ollama respondeu com status HTTP de erro."""

    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body}")


class OllamaParseError(OllamaProviderError):
    """Corpo da resposta não é JSON de objeto como esperado."""
