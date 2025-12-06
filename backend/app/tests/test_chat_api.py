import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # type: ignore  # noqa: E402

from app.main import app  # noqa: E402


def test_chat_endpoint_smoke():
    client = TestClient(app)
    resp = client.post("/api/v1/chat", json={"user_id": "u1", "message": "hello"})
    assert resp.status_code == 200
