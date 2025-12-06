import os

try:
    from pymilvus import (
        Collection,
        CollectionSchema,
        DataType,
        FieldSchema,
        connections,
    )
except Exception as exc:  # pragma: no cover - helper script
    raise SystemExit(f"pymilvus is required to run this script: {exc}")


def main() -> None:
    host = os.getenv("MILVUS_HOST", "localhost")
    port = os.getenv("MILVUS_PORT", "19530")
    collection_name = os.getenv("MILVUS_COLLECTION", "chat_history")

    connections.connect(alias="default", host=host, port=port)

    fields = [
        FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=128, is_primary=True, auto_id=False),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2048),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1536),
    ]
    schema = CollectionSchema(fields=fields, description="Chat history memory store")

    if Collection.exists(collection_name):  # type: ignore[attr-defined]
        print(f"Collection {collection_name} already exists")
        return

    collection = Collection(name=collection_name, schema=schema)
    collection.create_index(
        field_name="vector",
        index_params={"index_type": "IVF_FLAT", "metric_type": "IP", "params": {"nlist": 1024}},
    )
    collection.load()
    print(f"Created and loaded collection: {collection_name}")


if __name__ == "__main__":
    main()
