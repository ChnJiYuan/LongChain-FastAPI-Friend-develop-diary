import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # type: ignore  # noqa: E402

from app.api.v1 import deps  # noqa: E402
from app.main import app  # noqa: E402
from app.services.chains.chat_chain import ChatChain, ChatResult  # noqa: E402
from app.services.llm.router import LLMRouter  # noqa: E402
from app.services.memory.memory_service import MemoryContext, MemoryService  # noqa: E402


class StubChatChain(ChatChain):
    def __init__(self) -> None:
        pass

    async def run(self, user_id: str, message: str, images=None) -> ChatResult:  # type: ignore[override]
        return ChatResult(
            reply=f"echo:{message}",
            memori_context="profile block",
            milvus_chunks=["hit1", "hit2"],
            trace_id="trace-123",
        )


class StubMemoryService(MemoryService):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def retrieve_context(self, user_id: str, query: str) -> MemoryContext:  # type: ignore[override]
        self.calls.append((user_id, query))
        return MemoryContext(memori_context="PROFILE:demo", milvus_chunks=["h1", "h2"], stats={})


class StubLLMRouter(LLMRouter):
    def __init__(self) -> None:
        self.last_prompt: str | None = None

    async def generate(self, prompt: str, provider=None) -> str:  # type: ignore[override]
        self.last_prompt = prompt
        return "[stub reply]"


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


@pytest.fixture()
def client():
    return TestClient(app)


def test_chat_endpoint_returns_contract(client: TestClient):
    app.dependency_overrides[deps.get_chat_chain] = lambda: StubChatChain()
    resp = client.post("/api/v1/chat", json={"user_id": "u1", "message": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["reply"] == "echo:hello"
    assert data["memori_context"] == "profile block"
    assert data["milvus_chunks"] == ["hit1", "hit2"]
    assert data["trace_id"] == "trace-123"


def test_chat_rejects_blank_message(client: TestClient):
    app.dependency_overrides[deps.get_chat_chain] = lambda: StubChatChain()
    resp = client.post("/api/v1/chat", json={"user_id": "u1", "message": "   "})
    assert resp.status_code == 422
    assert "must not be blank" in resp.text


def test_chat_integrates_memory_and_llm_prompt(client: TestClient):
    stub_mem = StubMemoryService()
    stub_llm = StubLLMRouter()
    chain = ChatChain(memory_service=stub_mem, llm_router=stub_llm)
    app.dependency_overrides[deps.get_chat_chain] = lambda: chain

    resp = client.post("/api/v1/chat", json={"user_id": "user-42", "message": "Hi there"})
    assert resp.status_code == 200
    # Memory service got the call with trimmed inputs
    assert stub_mem.calls == [("user-42", "Hi there")]
    # LLM prompt should include memori context, milvus hits, and user message
    assert stub_llm.last_prompt is not None
    assert "PROFILE:demo" in stub_llm.last_prompt
    assert "- h1" in stub_llm.last_prompt and "- h2" in stub_llm.last_prompt
    assert "User:\nHi there" in stub_llm.last_prompt
    # Response body still follows contract
    data = resp.json()
    assert data["memori_context"] == "PROFILE:demo"
    assert data["milvus_chunks"] == ["h1", "h2"]
    assert data["reply"] == "[stub reply]"
