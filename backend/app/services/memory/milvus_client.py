import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

try:
    from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, MilvusException, connections
except Exception:  # pragma: no cover - optional dependency
    Collection = None  # type: ignore
    CollectionSchema = None  # type: ignore
    FieldSchema = None  # type: ignore
    DataType = None  # type: ignore
    MilvusException = Exception  # type: ignore
    connections = None  # type: ignore


class MilvusClient:
    """Best-effort Milvus wrapper with an in-memory fallback for local dev."""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        collection: str,
        use_tls: bool = False,
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.collection = collection
        self.use_tls = use_tls
        self._collection_handle: Optional[Any] = None
        self._local_store: List[Tuple[str, str, Dict[str, Any], List[float]]] = []

    def connect(self) -> None:
        if connections is None:
            logger.warning("pymilvus not installed; using in-memory store only")
            return
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=str(self.port),
                user=self.user,
                password=self.password,
                secure=self.use_tls,
            )
            logger.info("Connected to Milvus at %s:%s", self.host, self.port)
            self._ensure_collection()
        except MilvusException as exc:
            logger.error("Milvus connection failed: %s", exc)
            raise

    def _ensure_collection(self) -> None:
        if Collection is None:
            return
        try:
            collection = Collection(self.collection)
            self._collection_handle = collection
            return
        except MilvusException:
            pass

        logger.info("Creating Milvus collection %s", self.collection)
        fields = [
            FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=128, is_primary=True, auto_id=False),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1536),
        ]
        schema = CollectionSchema(fields=fields, description="Chat history")
        collection = Collection(name=self.collection, schema=schema)
        collection.create_index(
            field_name="vector",
            index_params={"index_type": "IVF_FLAT", "metric_type": "IP", "params": {"nlist": 1024}},
        )
        self._collection_handle = collection

    def upsert(self, user_id: str, content: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        if Collection is None or self._collection_handle is None:
            self._local_store.append((user_id, content, metadata or {}, embedding))
            logger.debug("Stored message in local Milvus fallback store")
            return
        self._collection_handle.insert([[user_id], [content], [embedding]])
        self._collection_handle.flush()

    def search(self, user_id: str, embedding: List[float], top_k: int = 5) -> List[str]:
        if Collection is None or self._collection_handle is None:
            # Return most recent messages for the user from fallback store
            hits = [rec[1] for rec in self._local_store if rec[0] == user_id]
            return hits[-top_k:]

        self._collection_handle.load()
        results = self._collection_handle.search(
            data=[embedding],
            anns_field="vector",
            param={"metric_type": "IP", "params": {"nprobe": 10}},
            limit=top_k,
            expr=f'user_id == "{user_id}"',
            output_fields=["content"],
        )
        return [hit.entity.get("content") for hit in results[0]]

    def drop_user(self, user_id: str) -> None:
        if Collection is None or self._collection_handle is None:
            self._local_store = [rec for rec in self._local_store if rec[0] != user_id]
            return
        expr = f'user_id == "{user_id}"'
        self._collection_handle.delete(expr=expr)

    def ping(self) -> bool:
        if Collection is None:
            return True  # fallback mode
        try:
            if self._collection_handle is None:
                self._ensure_collection()
            return True
        except MilvusException as exc:
            logger.error("Milvus ping failed: %s", exc)
            return False
