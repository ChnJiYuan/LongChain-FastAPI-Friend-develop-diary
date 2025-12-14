# Membot (LangChain + FastAPI Companion)

Membot is a dual-memory chat companion: Memori acts as a structured notebook for durable facts, while Milvus stores dense vector history for similarity recall. FastAPI exposes the orchestration layer, LangChain stitches memories into prompts, and a React/Vite frontend provides the chat surface.

## Repository Map
- `backend/`: FastAPI service, LangChain chains, memory clients, and API routers.
- `frontend/`: Vite + React UI (dev server in Dockerfile).
- `infra/`: Milvus compose snippet and helper scripts (for local bootstrapping).
- `docs/`, `DiaryDocument/`, `EverydayStep/`: design notes and daily logs.
- `docker-compose.yml`: Brings up Milvus stack + backend + frontend.
- `.env.example`, `requirements.txt`: environment template and Python deps.

## Architecture (fast path)
1) API ingress: FastAPI (`backend/app/main.py`) receives chat and admin routes; CORS enabled for the web UI.
2) Memory write: user turns are written to Memori (structured facts) and Milvus (vector embeddings; fallback in-memory store when Milvus is absent).
3) Context build: Memori facts + Milvus k-NN results feed prompt assembly in LangChain (`services/chains/chat_chain.py` and `services/llm/prompts.py`).
4) LLM call: routes to OpenAI or Ollama clients (`services/llm`), returning the answer along with referenced memories.
5) Frontend: React app calls the FastAPI endpoints and renders conversation + retrieved context.
6) Image generation (planned): local Stable Diffusion or cloud Gemini (Banana) via unified image API (`IMAGE_PROVIDER` controls local/cloud/auto).

## Tooling & Services
- `FastAPI` + `uvicorn`: HTTP API and server.
- `LangChain`, `langchain-openai`: prompt/composition utilities and provider clients.
- `Memori` SDK (stubbed): structured notebook storage for user profile, facts, and long-term notes.
- `Milvus` + `MinIO` + `etcd`: vector database stack (compose services `milvus`, `minio`, `etcd`); fallback in-memory vector store when unavailable.
- `OpenAI API` or `Ollama` (local models): LLM + embeddings providers; configurable via `.env`.
- Image gen providers (planned): local Stable Diffusion (`SD_BASE_URL`) and cloud Gemini/Banana (`GEMINI_BASE_URL`, `GEMINI_API_KEY`), selectable via `IMAGE_PROVIDER`.
- `Docker Compose`: one command to run Milvus, storage, backend, and frontend together.
- `pytest`: backend smoke tests.
- `React` + `Vite`: SPA frontend, served via the dev server in Docker.

## Memory Split (from 2025-12-06 diary)
- **Memori = structured notebook**: user profile, key facts, long-term preferences, events; stays human-readable.
- **Milvus = vector warehouse**: dense embedding search across chat history, image captions, and notes for “have I said this before?” recall.
- Flow: write to both stores → fetch Memori facts → embed query and search Milvus → merge contexts → call LLM.

## Getting Started
1) `cp .env.example .env` and fill OpenAI/Ollama/Memori/Milvus settings (see `docs/env.md` for all variables).
2) `docker-compose up -d` to start Milvus + MinIO + backend + frontend.
3) (Optional) `python infra/scripts/init_milvus.py` to create the chat collection and index.
4) Local dev without Docker: `uvicorn app.main:app --reload --app-dir backend`.
5) Tests: `pytest backend/app/tests`.
6) Postgres (dev only): Compose seeds `postgres` service using `POSTGRES_*` in `.env` and runs `infra/db/init.sql`. Replace creds and use a managed DB for prod.

## API Contract (v1)
- `POST /api/v1/chat`: body `{ "user_id": "...", "message": "...", "images": ["<base64>"] }` (user_id/message are trimmed; 1-128 chars for user_id, 1-4000 chars for message; up to 5 images, no empty strings). Returns `{ reply, memori_context, milvus_chunks, trace_id }`. Optional header `X-API-Key` if configured.
- `GET /api/v1/memory/{user_id}`: returns Memori/Milvus context snapshot for debugging.
- `GET /api/v1/memory/health`: health check for Memori/Milvus connectivity and current embedder.
- `POST /api/v1/memory/{user_id}`: write content into Memori and Milvus.

## Notes
- Memori client methods are placeholders; swap in the official SDK when available.
- Frontend styling and API bindings live in `frontend/`; backend chains and memory clients are in `backend/app/services/`.
- The repo name in code can stay as-is; the product name is **Membot**.
