import asyncio

from app.services.chains.chat_chain import ChatChain
from app.services.llm.router import LLMRouter
from app.services.memory.memory_service import MemoryContext, MemoryService


class DummyMemory(MemoryService):
    def __init__(self) -> None:
        pass

    def retrieve_context(self, user_id: str, query: str) -> MemoryContext:  # type: ignore[override]
        return MemoryContext(memori_context="memo", milvus_chunks=["a"], stats={})


class DummyRouter(LLMRouter):
    def __init__(self) -> None:
        pass

    async def generate(self, prompt: str, provider=None) -> str:  # type: ignore[override]
        return prompt[:10]


def test_chat_chain_runs():
    chain = ChatChain(memory_service=DummyMemory(), llm_router=DummyRouter())
    result = asyncio.run(chain.run(user_id="u1", message="hello"))
    assert result.reply
    assert result.milvus_hits == ["a"]
