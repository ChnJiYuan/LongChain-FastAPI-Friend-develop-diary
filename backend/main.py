from fastapi import FastAPI

from backend.routers import agent_api, chat, generate, image, memory
from backend.config import settings

app = FastAPI(
    title="LongChain-FastAPI-Friend",
    description="AI companion chatbot backend (FastAPI + LangChain)",
    version="0.1.0",
)


@app.get("/healthz")
def health_check():
    return {"status": "ok", "device": settings.device}


def register_routes(api: FastAPI) -> None:
    api.include_router(chat.router, prefix="/chat", tags=["chat"])
    api.include_router(memory.router, prefix="/memory", tags=["memory"])
    api.include_router(image.router, prefix="/image", tags=["image"])
    api.include_router(generate.router, prefix="/generate", tags=["generate"])
    api.include_router(agent_api.router, prefix="/agent", tags=["agent"])


register_routes(app)


# For `uvicorn backend.main:app --reload`
__all__ = ["app"]
