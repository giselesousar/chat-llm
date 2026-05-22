from fastapi import FastAPI

from app.api.routes import completions

app = FastAPI(
    title="Inference API",
    version="0.1.0",
    description="API OpenAI-like de inferência (proxy para Ollama). Requer X-API-Key.",
    openapi_tags=[
        {"name": "openai", "description": "Chat completions."},
    ],
)
app.include_router(completions.router)


@app.get("/health", summary="Verificação de saúde")
def health() -> dict[str, str]:
    return {"status": "ok"}
