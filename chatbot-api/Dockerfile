FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml main.py ./
COPY app ./app
RUN pip install uv && uv sync --no-dev
RUN mkdir -p data
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
