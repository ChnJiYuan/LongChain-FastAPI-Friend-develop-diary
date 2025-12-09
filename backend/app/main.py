from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import admin, chat, health, memory
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.persistence.db import init_db


def create_app() -> FastAPI:
    """Create FastAPI app with core middleware and v1 routes."""
    configure_logging(settings.log_level)
    # Ensure relational tables exist in dev; production should run real migrations.
    init_db()

    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(chat.router, prefix=settings.api_prefix, tags=["chat"])
    app.include_router(memory.router, prefix=settings.api_prefix, tags=["memory"])
    app.include_router(admin.router, prefix=settings.api_prefix, tags=["admin"])

    return app


app = create_app()

# For `uvicorn app.main:app --reload`
__all__ = ["app", "create_app"]
