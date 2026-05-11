from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.deps import CurrentUserDep, OllamaProviderDep
from app.providers.ollama_exceptions import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaParseError,
)
from app.providers.openai_ollama_bridge import (
    ollama_to_openai,
    openai_chat_completion_request_to_ollama_payload,
)
from app.schemas.openai import ChatCompletionRequest

router = APIRouter(prefix="/v1", tags=["openai"])


@router.post("/chat/completions")
def create_chat_completion(
    payload: ChatCompletionRequest,
    provider: OllamaProviderDep,
    _: CurrentUserDep,
) -> JSONResponse:
    """Chat completions no contrato OpenAI; backend Ollama em ``OLLAMA_BASE_URL``."""
    try:
        ollama_body = openai_chat_completion_request_to_ollama_payload(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    try:
        ollama_raw = provider.chat_completions(ollama_body)
    except OllamaConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except OllamaHTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ollama retornou {exc.status_code}: {exc.body}",
        ) from exc
    except OllamaParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    openai_response = ollama_to_openai(ollama_raw, model=payload.model)
    return JSONResponse(content=openai_response)
