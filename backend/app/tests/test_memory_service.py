import pytest

from app.services.memory.memori_client import MemoriClient
from app.services.memory.memory_service import MemoryService, build_default_embedder
from app.services.memory.milvus_client import MilvusClient


def test_memory_service_records_and_retrieves():
    memori = MemoriClient(project_id="demo", api_key="", endpoint="http://localhost")
    milvus = MilvusClient(
        host="localhost",
        port=19530,
        user="root",
        password="Milvus",
        database="default",
        collection="chat_history",
    )
    service = MemoryService(memori_client=memori, milvus_client=milvus, embedder=build_default_embedder("test"))

    service.record_user_message("u1", "hello world")
    context = service.retrieve_context("u1", "hello")

    assert "Profile" in context.memori_context
    assert isinstance(context.milvus_chunks, list)


@pytest.mark.parametrize("model", ["foo-model", "bar-model"])
def test_placeholder_embedder_is_deterministic(model: str):
    embed = build_default_embedder(model)
    assert embed("same text") == embed("same text")
