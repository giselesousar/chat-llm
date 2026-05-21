class LLMProviderError(Exception):
    pass


class LLMConnectionError(LLMProviderError):
    pass


class LLMHTTPError(LLMProviderError):
    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body}")


class LLMParseError(LLMProviderError):
    pass
