import os

from fastapi import FastAPI

from app.api.routes import auth, chats
from app.db import Base, engine
from app.models import ChatMessage, ChatSession, User  # noqa: F401

app = FastAPI(
    title="Chatbot API",
    version="0.1.0",
    description="""
API de chatbot com JWT, sessões persistidas e REST `/chats`.

### Autenticação
1. `POST /auth/register` — criar conta
2. `POST /auth/login` — obter `access_token`
3. Enviar `Authorization: Bearer <token>` nas rotas protegidas

### Canal (`channel`)
`web` (padrão), `cli` ou `app` — metadado do chat (`POST /chats`).
    """.strip(),
    openapi_tags=[
        {
            "name": "auth",
            "description": "Registro e login com JWT.",
        },
        {
            "name": "chats",
            "description": "Conversas e mensagens para o frontend.",
        },
    ],
)
app.include_router(auth.router)
app.include_router(chats.router)


@app.get(
    "/health",
    summary="Verificação de saúde",
    response_description="Serviço operacional.",
)
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
def startup() -> None:
    from app.core.config import DATABASE_URL
    if DATABASE_URL.startswith("sqlite:///./"):
        os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
