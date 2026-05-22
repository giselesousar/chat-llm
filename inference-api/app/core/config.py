import os

LLM_BASE_URL = os.environ.get(
    "LLM_BASE_URL",
    os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
).rstrip("/")
LLM_TIMEOUT_SECONDS = float(
    os.environ.get("LLM_TIMEOUT_SECONDS", os.environ.get("OLLAMA_TIMEOUT_SECONDS", "120")),
)
INFERENCE_API_KEY = os.environ.get("INFERENCE_API_KEY", "dev-inference-key")
