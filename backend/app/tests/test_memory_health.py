import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # type: ignore  # noqa: E402

from app.api.v1 import deps  # noqa: E402
from app.main import app  # noqa: E402
from app.services.memory.memory_service import MemoryService  # noqa: E402


class StubMemoryService(MemoryService):
    def __init__(self) -> None:
        pass

    def health_check(self) -> dict:  # type: ignore[override]
        return {"memori": True, "milvus": False, "embedder": "stubbed"}


@pytest.fixture(autouse=True)
def override_memory_service():
    app.dependency_overrides[deps.get_memory_service] = lambda: StubMemoryService()
    yield
    app.dependency_overrides.pop(deps.get_memory_service, None)


def test_memory_health_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/memory/health")
    assert resp.status_code == 200
    assert resp.json() == {"memori": True, "milvus": False, "embedder": "stubbed"}
