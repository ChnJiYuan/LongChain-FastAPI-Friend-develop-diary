# Environment Configuration (Membot)

This repo uses a single `.env` file (copied from `.env.example`) consumed by `docker-compose`, the FastAPI backend, and the Vite frontend.

## Core
- `APP_ENV`: `dev` | `prod` controls logging and dev behaviours.
- `PROJECT_NAME`, `APP_VERSION`, `API_PREFIX`, `LOG_LEVEL`, `CORS_ORIGINS`.

## LLM / Embeddings
- `OPENAI_API_KEY`: required when using OpenAI.
- `LLM_MODEL`: e.g., `gpt-4.1` (or Ollama model if `LLM_PROVIDER=ollama`).
- `EMBEDDING_MODEL`: e.g., `text-embedding-3-large`.
- `EMBEDDING_DIM`: vector dimension; keep in sync with `EMBEDDING_MODEL` and Milvus schema (default 1536).
- `LLM_PROVIDER`: `openai` | `ollama` | `mock`.

## Memori (structured memory)
- `MEMORI_PROJECT_ID`, `MEMORI_API_KEY`, `MEMORI_ENDPOINT`.
- `MEMORI_STORAGE_URL` (optional, dev-only): set to a real DB DSN if you want Memori to persist via SQL; avoid SQLite in production.

## Stable Diffusion (local image gen)
- `SD_ENABLED`: toggle local SD usage.
- `SD_BASE_URL`: e.g., `http://host.docker.internal:7860` (Automatic1111 WebUI default).
- `SD_MODEL`: optional model/ checkpoint name if your SD API supports switching.

## Gemini / Banana (cloud image gen)
- `GEMINI_ENABLED`: toggle cloud image generation.
- `GEMINI_BASE_URL`: proxy/base URL to your Gemini/Banana endpoint.
- `GEMINI_API_KEY`: API key or auth token for the cloud service.
- `GEMINI_MODEL`: target model name.
- `IMAGE_PROVIDER`: `local` | `cloud` | `auto` (auto: try local first, fallback to cloud).

## Milvus (vector memory)
- `MILVUS_HOST`, `MILVUS_PORT`, `MILVUS_USER`, `MILVUS_PASSWORD`, `MILVUS_COLLECTION`, `MILVUS_DATABASE`, `MILVUS_TLS`.
- `EMBEDDING_DIM` is also read by `infra/scripts/init_milvus.py` to size the collection.

## App persistence (FastAPI)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`: used by Docker Compose to seed the Postgres container.
- `DATABASE_URL`: backend SQLAlchemy URL. For dev, defaults to `postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:${POSTGRES_PORT}/${POSTGRES_DB}`; override with strong creds for prod.

## Ollama (local LLM)
- `OLLAMA_BASE_URL`: typically `http://localhost:11434` when running Ollama locally.

## Frontend (Vite)
- `VITE_API_BASE_URL`: backend URL the SPA should call (e.g., `http://localhost:8000`).
- `VITE_API_KEY` (optional): if backend enforces `X-API-Key`, set the key so the frontend attaches it automatically.

## Docker usage
1) Copy `.env.example` to `.env` and fill secrets before running Docker.
2) `docker-compose up -d` starts Milvus + MinIO + backend + frontend (backend depends on Milvus health).
3) After Milvus is up, run `python infra/scripts/init_milvus.py` (uses `EMBEDDING_DIM` and `MILVUS_*` vars) to ensure the collection/index exists.
