import os

LLM_BASE_URL = os.environ.get(
    "LLM_BASE_URL",
    os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
).rstrip("/")
LLM_TIMEOUT_SECONDS = float(
    os.environ.get("LLM_TIMEOUT_SECONDS", os.environ.get("OLLAMA_TIMEOUT_SECONDS", "120")),
)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/app.db")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))

CHAT_MAX_MESSAGES = 50
CHAT_MAX_CONTENT_CHARS = 10_000
CHAT_DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

INFERENCE_BASE_URL = os.environ.get("INFERENCE_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
INFERENCE_API_KEY = os.environ.get("INFERENCE_API_KEY", "dev-inference-key")
