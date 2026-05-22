class InferenceClientError(Exception):
    pass


class InferenceConnectionError(InferenceClientError):
    pass


class InferenceHTTPError(InferenceClientError):
    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body}")


class InferenceParseError(InferenceClientError):
    pass
