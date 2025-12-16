# Membot (LangChain + FastAPI Companion)

Membot is a dual-memory chat companion: Memori holds structured facts while Milvus keeps dense vector history. FastAPI orchestrates, LangChain builds prompts, and a React/Vite (or Electron shell) frontend provides the UI. Local Stable Diffusion is supported for image generation.

## Repository Map
- `backend/`: FastAPI app, LangChain chains, memory/image clients, API routers.
- `frontend/`: Vite + React UI; Electron shell in `frontend/electron`.
- `infra/`: Milvus compose snippet and helper scripts.
- `docs/`, `DiaryDocument/`, `EverydayStep/`: design notes and daily logs.
- `docker-compose.yml`: Milvus stack + backend + frontend.
- `.env.example`, `requirements.txt`: env template and Python deps.

## Architecture (fast path)
1) API ingress: FastAPI (`backend/app/main.py`) receives chat/admin/image routes; CORS enabled for the web UI.
2) Memory write: user turns go to Memori (structured facts) and Milvus (vectors; in-memory fallback when Milvus is absent).
3) Context build: Memori facts + Milvus k-NN results feed prompt assembly (`services/chains/chat_chain.py`, `services/llm/prompts.py`).
4) LLM call: routes to OpenAI or Ollama clients (`services/llm`) and returns reply plus referenced memories.
5) Frontend: React app calls the API and renders conversation and retrieved context; Electron wraps it for desktop.
6) Image generation: local Stable Diffusion or cloud Gemini/Banana via unified image API (`IMAGE_PROVIDER` controls local/cloud/auto).

## Tooling & Services
- `FastAPI` + `uvicorn`
- `LangChain`, `langchain-openai`
- `Milvus` + `MinIO` + `etcd`
- `OpenAI` or `Ollama` for LLM + embeddings (configurable via `.env`)
- Stable Diffusion WebUI API (`SD_BASE_URL`) or cloud Gemini/Banana (`GEMINI_BASE_URL`, `GEMINI_API_KEY`)
- `Docker Compose` for one-command runtime; `pytest` for backend smoke tests; `React` + `Vite` for the SPA

## Getting Started (full stack via Docker)
Prereqs: Docker Desktop (WSL2 backend on Windows), Stable Diffusion WebUI running with API (`--api --listen --port 7860`) if you want local images.

1) Copy envs: `cp .env.example .env`, then fill secrets. Defaults in this repo:
   - API port: `API_PORT=18000`
   - API key: `MEMORI_API_KEY=qsnnb666` (frontend also reads `VITE_API_KEY`)
   - Local SD: `SD_ENABLED=true`, `SD_BASE_URL=http://host.docker.internal:7860`
   - Image persistence: `IMAGE_SAVE_DIR=./data/images` (mounted into the backend container)
2) Start services: `docker-compose up -d --build`  
   Brings up Milvus + MinIO + etcd + Postgres + backend (FastAPI) + frontend (Vite dev server on 5173).
3) Health checks (PowerShell examples):
   - API: `Invoke-RestMethod http://localhost:18000/health`
   - Memory: `Invoke-RestMethod -Headers @{ 'X-API-Key'='qsnnb666' } http://localhost:18000/api/v1/memory/health`
   - Image: `Invoke-RestMethod -Headers @{ 'X-API-Key'='qsnnb666' } http://localhost:18000/api/v1/image/health`
4) Frontend: open `http://localhost:5173`. The Image panel prompts SD/Gemini; results display inline, can be downloaded, and are saved to `data/images/`.
5) Direct image API smoke test:
   ```powershell
   $h=@{ 'Content-Type'='application/json'; 'X-API-Key'='qsnnb666' }
   $b=@{ prompt='a watercolor cat astronaut'; provider='local' } | ConvertTo-Json
   Invoke-RestMethod -Method Post -Uri http://localhost:18000/api/v1/image -Headers $h -Body $b
   ```
   Response includes `image_base64`, `trace_id`, `provider`, and `file_path` on disk.
6) Optional Milvus bootstrap: `python infra/scripts/init_milvus.py` (uses `MILVUS_*` and `EMBEDDING_DIM` from `.env`).
7) Tests: `pytest backend/app/tests`.

## Local development (without full compose)
- Backend only: `uvicorn app.main:app --reload --app-dir backend --port 8000` (adjust `VITE_API_BASE_URL` if needed).
- Frontend only: `cd frontend && npm install && npm run dev -- --host --port 5173`.
- Electron shell: from `frontend/` run `npm run electron:dev`; build with `npm run electron:build` (artifacts in `frontend/release/`).
- Local SD WebUI: `python webui.py --api --listen --port 7860` or set `COMMANDLINE_ARGS="--api --listen --port 7860"` before `webui-user.bat`.

## API Contract (v1)
- `POST /api/v1/chat`: body `{ "user_id": "...", "message": "...", "images": ["<base64>"] }`; returns `{ reply, memori_context, milvus_chunks, trace_id }`. Optional header `X-API-Key`.
- `GET /api/v1/memory/{user_id}`: returns Memori/Milvus snapshot.
- `GET /api/v1/memory/health`: health for Memori/Milvus.
- `POST /api/v1/memory/{user_id}`: write content into Memori and Milvus.
- `GET /api/v1/image/health`: SD/Gemini health.
- `POST /api/v1/image`: generate image; returns `{ image_base64, provider, trace_id, file_path }`.

## Notes
- Memori client methods are placeholders; swap in the official SDK when available.
- Backend image responses also save PNGs to `IMAGE_SAVE_DIR`; UI offers download plus shows saved path.
- The repo name can stay as-is; the product name is **Membot**.
