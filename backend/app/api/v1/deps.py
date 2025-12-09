from functools import lru_cache

from app.core.config import settings
from app.services.chains.chat_chain import ChatChain
from app.services.llm.ollama_client import OllamaClient
from app.services.llm.openai_client import OpenAIClient
from app.services.llm.router import LLMRouter
from app.services.memory.memori_client import MemoriClient
from app.services.memory.memory_service import MemoryService, build_default_embedder
from app.services.memory.milvus_client import MilvusClient


@lru_cache
def get_memori_client() -> MemoriClient:
    return MemoriClient(
        project_id=settings.memori_project_id,
        api_key=settings.memori_api_key,
        endpoint=settings.memori_endpoint,
        storage_url=settings.memori_storage_url,
        openai_api_key=settings.openai_api_key,
    )


@lru_cache
def get_milvus_client() -> MilvusClient:
    return MilvusClient(
        host=settings.milvus_host,
        port=settings.milvus_port,
        user=settings.milvus_user,
        password=settings.milvus_password,
        database=settings.milvus_database,
        collection=settings.milvus_collection,
        use_tls=settings.milvus_tls,
    )


@lru_cache
def get_memory_service() -> MemoryService:
    return MemoryService(
        memori_client=get_memori_client(),
        milvus_client=get_milvus_client(),
        embedder=build_default_embedder(settings.embedding_model),
    )


@lru_cache
def get_llm_router() -> LLMRouter:
    return LLMRouter(
        default_provider=settings.llm_provider,
        openai_client=OpenAIClient(
            api_key=settings.openai_api_key, model=settings.llm_model
        ),
        ollama_client=OllamaClient(
            base_url=settings.ollama_base_url, model=settings.llm_model
        ),
    )


@lru_cache
def get_chat_chain() -> ChatChain:
    return ChatChain(
        memory_service=get_memory_service(),
        llm_router=get_llm_router(),
    )


__all__ = [
    "get_chat_chain",
    "get_llm_router",
    "get_memori_client",
    "get_memory_service",
    "get_milvus_client",
]
