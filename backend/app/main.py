from fastapi import FastAPI

from app.api.routes import auth, chat
from app.db import Base, engine
from app.models import ChatMessage, ChatSession, User, UserMemory  # noqa: F401

app = FastAPI(
    title="Inferência (OpenAI-like → Ollama)",
    version="0.1.0",
)
app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
