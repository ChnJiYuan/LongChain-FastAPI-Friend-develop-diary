import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # type: ignore  # noqa: E402

from app.api.v1 import deps  # noqa: E402
from app.main import app  # noqa: E402
from app.services.chains.chat_chain import ChatResult, ChatChain  # noqa: E402


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


@pytest.fixture(autouse=True)
def override_chat_chain():
    app.dependency_overrides[deps.get_chat_chain] = lambda: StubChatChain()
    yield
    app.dependency_overrides.pop(deps.get_chat_chain, None)


def test_chat_endpoint_returns_contract():
    client = TestClient(app)
    resp = client.post("/api/v1/chat", json={"user_id": "u1", "message": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["reply"] == "echo:hello"
    assert data["memori_context"] == "profile block"
    assert data["milvus_chunks"] == ["hit1", "hit2"]
    assert data["trace_id"] == "trace-123"


def test_chat_rejects_blank_message():
    client = TestClient(app)
    resp = client.post("/api/v1/chat", json={"user_id": "u1", "message": "   "})
    assert resp.status_code == 422
    assert "must not be blank" in resp.text
