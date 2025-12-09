from app.services.memory.milvus_client import MilvusClient


def test_milvus_client_fallback_store():
    client = MilvusClient(
        host="localhost",
        port=19530,
        user="root",
        password="Milvus",
        database="default",
        collection="chat_history",
    )

    # Without connection/_collection_handle, it should use the in-memory store
    client.upsert("u1", "hello", [0.1, 0.2], {"k": "v"})
    client.upsert("u1", "later message", [0.3])
    client.upsert("u2", "other user", [0.5])

    hits = client.search("u1", [0.2], top_k=1)
    assert hits == ["later message"]  # most recent

    client.drop_user("u1")
    assert client.search("u1", [0.1]) == []
