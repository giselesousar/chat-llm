from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.deps import ChatOrchestratorDep, CurrentUserDep
from app.inference_api.exceptions import LLMConnectionError, LLMHTTPError, LLMParseError
from app.schemas.openai import ChatCompletionRequest

router = APIRouter(prefix="/v1", tags=["openai"])


@router.post("/chat/completions")
def create_chat_completion(
    payload: ChatCompletionRequest,
    orchestrator: ChatOrchestratorDep,
    user: CurrentUserDep,
) -> JSONResponse:
    """Chat completions stateful no contrato OpenAI-like."""
    try:
        result = orchestrator.handle(payload, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LLMConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except LLMHTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Servidor de inferência retornou {exc.status_code}: {exc.body}",
        ) from exc
    except LLMParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return JSONResponse(content=result.response)
