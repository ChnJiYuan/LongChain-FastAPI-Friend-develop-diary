import os
import sys

try:
    from pymilvus import (
        Collection,
        CollectionSchema,
        DataType,
        FieldSchema,
        connections,
        utility,
    )
except Exception as exc:  # pragma: no cover - helper script
    raise SystemExit(f"pymilvus is required to run this script: {exc}")


def health_check(alias: str) -> None:
    try:
        version = utility.get_server_version()
        print(f"[milvus] connected (server_version={version})")
    except Exception as exc:
        raise SystemExit(f"[milvus] health check failed: {exc}")


def ensure_collection(name: str, dim: int) -> None:
    if utility.has_collection(name):
        print(f"[milvus] collection {name} already exists")
        return

    fields = [
        FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=128, is_primary=True, auto_id=False),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2048),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
    ]
    schema = CollectionSchema(fields=fields, description="Chat history memory store")

    collection = Collection(name=name, schema=schema)
    collection.create_index(
        field_name="vector",
        index_params={"index_type": "IVF_FLAT", "metric_type": "IP", "params": {"nlist": 1024}},
    )
    collection.load()
    print(f"[milvus] created and loaded collection: {name} (dim={dim})")


def main() -> None:
    host = os.getenv("MILVUS_HOST", "localhost")
    port = os.getenv("MILVUS_PORT", "19530")
    collection_name = os.getenv("MILVUS_COLLECTION", "chat_history")
    dim = int(os.getenv("EMBEDDING_DIM", "1536"))

    print(f"[milvus] connecting to {host}:{port}")
    connections.connect(alias="default", host=host, port=port)
    health_check(alias="default")
    ensure_collection(collection_name, dim=dim)


if __name__ == "__main__":
    main()
