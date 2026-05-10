# Chat-LLM

Projeto de exemplo do curso: APIs de inferência e chatbots.

A API em `backend/` é FastAPI com autenticação e chat no estilo OpenAI, usando [Ollama](https://ollama.com/) como motor de inferência.

## Requisitos

- Python 3.11 ou superior
- [uv](https://docs.astral.sh/uv/) (recomendado) ou `pip`

## Instalação

Com o diretório atual em `chat-llm/`:

```bash
cd backend
uv sync
```

## Executar

```bash
cd backend
uv run uvicorn main:app --reload
```

(Os comandos acima pressupõem que, após o `cd`, você está em `chat-llm/backend/`.)

- API: `http://127.0.0.1:8000`
- Documentação interativa: `http://127.0.0.1:8000/docs`
- Saúde: `GET /health`

## Variáveis de ambiente (opcionais)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `OLLAMA_BASE_URL` | URL do Ollama | `http://localhost:11434` |
| `OLLAMA_TIMEOUT_SECONDS` | Timeout das chamadas ao Ollama | `120` |
| `DATABASE_URL` | URL SQLAlchemy (ex.: SQLite) | `sqlite:///./data/app.db` |
| `JWT_SECRET_KEY` | Chave para assinar tokens JWT | `secret` |
| `JWT_EXPIRE_MINUTES` | Validade do token em minutos | `60` |

O SQLite usa por padrão o arquivo em `backend/data/` (pastas `data/` e `*.db` costumam estar no `.gitignore`). Crie `data/` se necessário; na subida da aplicação as tabelas são criadas.

## Ollama

Tenha o [Ollama](https://ollama.com/) em execução localmente ou ajuste `OLLAMA_BASE_URL` para o host correto.
