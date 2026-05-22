import secrets

from fastapi import Header, HTTPException, status

from app.core.config import INFERENCE_API_KEY


def verify_inference_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    if not INFERENCE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INFERENCE_API_KEY não configurada no servidor",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, INFERENCE_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida ou ausente",
        )
