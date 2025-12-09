import types

import app.services.memory.memori_client as mc


class FakeMemori:
    def __init__(self, project_id: str, api_key: str, endpoint: str, conn=None) -> None:
        self.project_id = project_id
        self.api_key = api_key
        self.endpoint = endpoint
        self.conn = conn
        self.saved = []
        self.queries = []
        self.resets = []
        # minimal openai wrapper to accept register()
        self.openai = types.SimpleNamespace(registered=False, register=self._register)

    def _register(self, client) -> None:
        self.openai.registered = True  # type: ignore[attr-defined]
        self.openai.client = client  # type: ignore[attr-defined]

    def save(self, user_id: str, text: str, metadata=None) -> None:
        self.saved.append((user_id, text, metadata or {}))

    def query(self, user_id: str, prompt: str):
        self.queries.append((user_id, prompt))
        if "profile" in prompt:
            return {"name": "Ada", "plan": "demo"}
        return ["did something great"]

    def reset(self, user_id: str) -> None:
        self.resets.append(user_id)


def test_memori_client_fallback_without_sdk(monkeypatch):
    monkeypatch.setattr(mc, "Memori", None)
    client = mc.MemoriClient(project_id="p1", api_key="", endpoint="http://local")

    # no SDK -> fallback strings and no exceptions
    assert client.query_profile("u1") == mc.FALLBACK_PROFILE
    assert client.query_recent_facts("u1") == mc.FALLBACK_FACTS
    client.save_note("u1", "hello")  # should not raise
    client.reset_user("u1")  # should not raise


def test_memori_client_uses_sdk(monkeypatch):
    monkeypatch.setattr(mc, "Memori", FakeMemori)
    # avoid OpenAI registration in test
    client = mc.MemoriClient(project_id="p2", api_key="key", endpoint="http://local", openai_api_key=None)

    assert isinstance(client._client, FakeMemori)

    client.save_note("u1", "hello", metadata={"x": 1})
    assert client._client.saved == [("u1", "hello", {"x": 1})]  # type: ignore[union-attr]

    profile = client.query_profile("u1")
    facts = client.query_recent_facts("u1")
    assert "Ada" in profile
    assert "did something great" in facts

    client.reset_user("u1")
    assert client._client.resets == ["u1"]  # type: ignore[union-attr]
