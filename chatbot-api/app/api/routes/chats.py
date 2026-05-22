from fastapi import APIRouter, HTTPException, status

from app.api.deps import ChatServiceDep, CurrentUserDep
from app.chatbot_backend.chat_service import ChatService
from app.clients.exceptions import InferenceConnectionError, InferenceHTTPError, InferenceParseError
from app.core.exceptions import ChatNotFoundError
from app.models.chat_message import ChatMessage as ChatMessageModel
from app.schemas.chats import (
    ChatCreateRequest,
    ChatListResponse,
    ChatRead,
    ChatSummary,
    MessageListResponse,
    MessageRead,
    SendMessageRequest,
    SendMessageResponse,
)

router = APIRouter(prefix="/chats", tags=["chats"])


def _session_preview(session, repo_messages: list[ChatMessageModel]) -> str | None:
    if not repo_messages:
        return None
    last = repo_messages[-1]
    text = (last.content or "")[:120]
    return text or None


def _map_inference_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, ValueError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, InferenceConnectionError):
        return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    if isinstance(exc, InferenceHTTPError):
        if exc.status_code == 401:
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de inferência indisponível (configuração)",
            )
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Serviço de inferência retornou {exc.status_code}: {exc.body}",
        )
    if isinstance(exc, InferenceParseError):
        return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    raise exc


@router.get("", response_model=ChatListResponse, summary="Listar chats do usuário")
def list_chats(
    chat_service: ChatServiceDep,
    user: CurrentUserDep,
) -> ChatListResponse:
    sessions = chat_service.list_chats(user)
    items: list[ChatSummary] = []
    for s in sessions:
        _, messages = chat_service.list_messages(s.session_id, user)
        items.append(
            ChatSummary(
                chat_id=s.session_id,
                channel=s.channel,  # type: ignore[arg-type]
                created_at=s.created_at,
                updated_at=s.updated_at,
                preview=_session_preview(s, messages),
            )
        )
    return ChatListResponse(items=items)


@router.post("", response_model=ChatRead, status_code=status.HTTP_201_CREATED, summary="Criar chat")
def create_chat(
    payload: ChatCreateRequest,
    chat_service: ChatServiceDep,
    user: CurrentUserDep,
) -> ChatRead:
    session = chat_service.create_chat(
        user,
        channel=payload.channel,
        chat_id=payload.chat_id,
    )
    chat_service._db.commit()
    chat_service._db.refresh(session)
    return ChatRead(
        chat_id=session.session_id,
        channel=session.channel,  # type: ignore[arg-type]
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/{chat_id}", response_model=ChatRead, summary="Obter metadados do chat")
def get_chat(
    chat_id: str,
    chat_service: ChatServiceDep,
    user: CurrentUserDep,
) -> ChatRead:
    try:
        session = chat_service.get_chat(chat_id, user)
    except ChatNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado") from exc
    return ChatRead(
        chat_id=session.session_id,
        channel=session.channel,  # type: ignore[arg-type]
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Apagar chat")
def delete_chat(
    chat_id: str,
    chat_service: ChatServiceDep,
    user: CurrentUserDep,
) -> None:
    try:
        chat_service.delete_chat(chat_id, user)
    except ChatNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado") from exc


@router.get("/{chat_id}/messages", response_model=MessageListResponse, summary="Histórico de mensagens")
def get_messages(
    chat_id: str,
    chat_service: ChatServiceDep,
    user: CurrentUserDep,
) -> MessageListResponse:
    try:
        session, messages = chat_service.list_messages(chat_id, user)
    except ChatNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado") from exc
    return MessageListResponse(
        chat_id=session.session_id,
        messages=[MessageRead.model_validate(m) for m in messages],
    )


@router.post(
    "/{chat_id}/messages",
    response_model=SendMessageResponse,
    summary="Enviar mensagem e obter resposta do assistente",
)
def send_message(
    chat_id: str,
    payload: SendMessageRequest,
    chat_service: ChatServiceDep,
    user: CurrentUserDep,
) -> SendMessageResponse:
    try:
        session = chat_service.get_chat(chat_id, user)
    except ChatNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado") from exc

    from app.schemas.openai import ChatCompletionRequest, ChatMessage

    messages: list[ChatMessage] = []
    if payload.system_prompt:
        messages.append(ChatMessage(role="system", content=payload.system_prompt))
    messages.append(ChatMessage(role="user", content=payload.content))
    request = ChatCompletionRequest(
        model=payload.model,
        messages=messages,
        session_id=chat_id,
        channel=session.channel,  # type: ignore[arg-type]
        stream=False,
    )
    try:
        result = chat_service.handle(request, user)
    except Exception as exc:
        raise _map_inference_errors(exc) from exc

    rows = chat_service._repo.list_messages(session.id)
    user_row = next((m for m in reversed(rows) if m.role == "user"), None)
    assistant_row = next((m for m in reversed(rows) if m.role == "assistant"), None)
    if user_row is None or assistant_row is None:
        raise HTTPException(status_code=500, detail="Mensagens não persistidas")

    return SendMessageResponse(
        chat_id=chat_id,
        user_message=MessageRead.model_validate(user_row),
        assistant_message=MessageRead.model_validate(assistant_row),
        latency_ms=result.metadata.latency_ms,
        context_window_size=result.metadata.context_window_size,
        context_strategy=result.metadata.context_strategy,
    )
