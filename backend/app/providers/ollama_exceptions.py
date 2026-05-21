class OllamaProviderError(Exception):
    pass


class OllamaConnectionError(OllamaProviderError):
    pass


class OllamaHTTPError(OllamaProviderError):
    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body}")


class OllamaParseError(OllamaProviderError):
    pass
