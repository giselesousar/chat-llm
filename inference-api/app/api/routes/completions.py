from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_completion_service
from app.core.exceptions import LLMConnectionError, LLMHTTPError, LLMParseError
from app.core.security import verify_inference_api_key
from app.schemas.openai import ChatCompletionRequest, ChatCompletionResponse
from app.services.completion import CompletionService

router = APIRouter(prefix="/v1", tags=["openai"], dependencies=[Depends(verify_inference_api_key)])


def _raise_http_from_llm(exc: Exception) -> None:
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if isinstance(exc, LLMConnectionError):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    if isinstance(exc, LLMHTTPError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Servidor LLM retornou {exc.status_code}: {exc.body}",
        ) from exc
    if isinstance(exc, LLMParseError):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    raise exc


@router.post(
    "/chat/completions",
    response_model=None,
    summary="Criar chat completion",
    responses={
        200: {
            "description": "JSON (`stream=false`) ou SSE (`stream=true`).",
            "content": {
                "application/json": {},
                "text/event-stream": {},
            },
        },
        400: {"description": "Payload inválido."},
        401: {"description": "API key ausente ou inválida."},
        502: {"description": "Falha ao contactar Ollama."},
    },
)
def create_chat_completion(
    payload: ChatCompletionRequest,
    service: CompletionService = Depends(get_completion_service),
) -> ChatCompletionResponse | StreamingResponse:
    if payload.stream:
        try:
            return StreamingResponse(
                service.stream(payload),
                media_type="text/event-stream",
            )
        except Exception as exc:
            _raise_http_from_llm(exc)

    try:
        result = service.create(payload)
    except Exception as exc:
        _raise_http_from_llm(exc)
    return ChatCompletionResponse.model_validate(result)
