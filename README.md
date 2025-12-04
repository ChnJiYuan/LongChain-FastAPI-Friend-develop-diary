# LongChain-FastAPI-Friend Develop Diary
A development log for building an AI companion chatbot using LangChain and FastAPI. This repo tracks architecture decisions, backend implementation, memory systems, RAG over real chat logs, and multimodal features (image analysis and generation). Status: early design draft.

## Repository layout
LongChain-FastAPI-Friend/
  backend/
    main.py                FastAPI entry
    config.py              Model configs and GPU detection
    routers/
      chat.py              Text chat API
      memory.py            User memory APIs (profile, recall)
      image.py             Image upload and analysis
      generate.py          Image generation API
    chains/
      conversation.py      LangChain conversational chain
      rag.py               RAG pipeline using chat logs
      vision.py            Image understanding chain
      agent.py             Tool-calling chain
      multimodal.py        Text + image combined reasoning
    gpu_inference/         CUDA-accelerated models
      local_llm.py         Local LLM running on GPU
      sd_generator.py      Stable Diffusion image generator
      utils.py             GPU utilities and model loaders
    db/
      chroma/              Vector store for RAG
      user_profile.json    Long-term memory data
    utils/
      image_utils.py       Image preprocessing helpers
      prompts.py           Prompt templates
      logging.py           Structured logging setup
  docs/
    architecture.md        High-level design
    development-diary.md   Build notes and experiments
    prompt-design.md       Prompting strategies
  examples/
    api-demo.ipynb         Demo notebook
  tests/
    README.md              Test plan and coverage notes
  frontend/               React UI scaffold (src/, public/, package.json)

## Local environment snapshot (2025-12-02)
- Python/Conda: Python 3.13.5, conda 24.11.3.
- GPU/CUDA: RTX 5070 Ti, driver 581.80, CUDA 13.0 (`nvidia-smi` OK, 16 GB VRAM).
- Hugging Face cache: `bert-base-uncased`, `openai/clip-vit-large-patch14`, `t5-small` in `C:\Users\USER\.cache\huggingface\hub`.
- Image generation: Stable Diffusion WebUI at `D:\UniWorkSpace\WorkPlace4Future\Stable-diffussion\stable-diffusion-webui` with models `dreamshaper_8.safetensors`, `majicmixRealistic_v7.safetensors`, `realisticVisionV60B1_v51HyperVAE.safetensors`; SDXL Refiner weights in `D:\UniWorkSpace\WorkPlace4Future\Stable-diffussion\stable-diffusion-xl-refiner-1.0` (`sd_xl_refiner_1.0*.safetensors`).
- Docker: Docker Desktop installed (`Docker version 28.5.1`); daemon currently not running (cannot reach `dockerDesktopLinuxEngine`).
- PostgreSQL/pgAdmin: installed in `D:\postgre` (pgAdmin 4 at `D:\postgre\pgAdmin 4\runtime\pgAdmin4.exe`, data directory `D:\postgre\data`).

## CUDA integration
- The planned `gpu_inference/` components (LLM + SD) can use the available RTX 5070 Ti; ensure PyTorch builds match CUDA 13.0.
- Stable Diffusion assets above can be wired into `sd_generator.py` (point to the WebUI models dir or load via diffusers).
- For RAG/LLM acceleration, enable `torch.cuda.is_available()` checks in `config.py` and prefer GPU-backed embeddings/inference when present.

## Scaffold status (2025-12-02)
- Backend: FastAPI app (`backend/main.py`) with stub routers for chat/memory/image/generate/agent; config has device/paths and SD model dir pointing to local WebUI weights.
- Frontend: React scaffold placeholders (`frontend/src`, `public`, `package.json`), pending toolchain (Vite/CRA) and styling setup.
- Docs/examples/tests: placeholder files created per layout.


## Development Milestones

- **Milestone 1:** Local LLM chat (partially complete) - add health checks and model configuration
- **Milestone 2:** RAG/tool calling demo integration - connect frontend and backend
- **Milestone 3:** Session management + error handling + basic tests - improve README
- **Milestone 4:** Optional cloud model switching and containerized deployment scripts