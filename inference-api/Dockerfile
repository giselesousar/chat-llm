FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml main.py ./
COPY app ./app
RUN pip install uv && uv sync --no-dev
EXPOSE 8001
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
