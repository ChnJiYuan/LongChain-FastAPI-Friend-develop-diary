import os
from dataclasses import dataclass, field
from typing import List


def _get_list(value: str, default: List[str]) -> List[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass
class Settings:
    project_name: str = os.getenv("PROJECT_NAME", "langchain-fastapi-companion")
    version: str = os.getenv("APP_VERSION", "0.1.0")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    environment: str = os.getenv("APP_ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # openai | ollama | mock

    sd_enabled: bool = os.getenv("SD_ENABLED", "false").lower() == "true"
    sd_base_url: str = os.getenv("SD_BASE_URL", "http://localhost:7860")
    sd_model: str = os.getenv("SD_MODEL", "")

    gemini_enabled: bool = os.getenv("GEMINI_ENABLED", "false").lower() == "true"
    gemini_base_url: str = os.getenv("GEMINI_BASE_URL", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "")
    image_provider: str = os.getenv("IMAGE_PROVIDER", "auto")  # local | cloud | auto
    image_save_dir: str = os.getenv("IMAGE_SAVE_DIR", "./data/images")

    memori_project_id: str = os.getenv("MEMORI_PROJECT_ID", "companion-assistant")
    memori_api_key: str = os.getenv("MEMORI_API_KEY", "")
    memori_endpoint: str = os.getenv("MEMORI_ENDPOINT", "https://api.memori.local")
    memori_storage_url: str = os.getenv("MEMORI_STORAGE_URL", "")  # optional; set for local dev only

    milvus_host: str = os.getenv("MILVUS_HOST", "localhost")
    milvus_port: int = int(os.getenv("MILVUS_PORT", "19530"))
    milvus_user: str = os.getenv("MILVUS_USER", "root")
    milvus_password: str = os.getenv("MILVUS_PASSWORD", "Milvus")
    milvus_collection: str = os.getenv("MILVUS_COLLECTION", "chat_history")
    milvus_database: str = os.getenv("MILVUS_DATABASE", "default")
    milvus_tls: bool = os.getenv("MILVUS_TLS", "false").lower() == "true"

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    cors_origins: List[str] = field(
        default_factory=lambda: _get_list(
            os.getenv("CORS_ORIGINS", ""), ["http://localhost:3000", "http://localhost:5173"]
        )
    )

    @property
    def is_dev(self) -> bool:
        return self.environment.lower() in {"dev", "development", "local"}


settings = Settings()

__all__ = ["settings", "Settings"]
