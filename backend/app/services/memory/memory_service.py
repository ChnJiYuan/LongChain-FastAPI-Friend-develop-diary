import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from app.services.memory.memori_client import MemoriClient
from app.services.memory.milvus_client import MilvusClient

logger = logging.getLogger(__name__)

Embedder = Callable[[str], List[float]]


@dataclass
class MemoryContext:
    memori_context: str
    milvus_chunks: List[str]
    stats: Dict[str, Any]


def build_default_embedder(model_name: str) -> Embedder:
    """Simple deterministic embedder placeholder."""

    def _embed(text: str) -> List[float]:
        tokens = text.split()
        return [float((hash(tok) % 1000) / 1000.0) for tok in tokens][:64] or [0.0]

    _embed.__name__ = f"placeholder_embedder_{model_name}"
    return _embed


class MemoryService:
    """Coordinate Memori (structured) + Milvus (vector) memory operations."""

    def __init__(
        self,
        memori_client: MemoriClient,
        milvus_client: MilvusClient,
        embedder: Optional[Embedder] = None,
    ) -> None:
        self.memori = memori_client
        self.milvus = milvus_client
        self.embed = embedder or build_default_embedder("default")
        try:
            self.milvus.connect()
        except Exception as exc:  # pragma: no cover - connection best effort
            logger.warning("Milvus connection skipped: %s", exc)

    def record_user_message(
        self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        logger.debug("Recording message for user=%s", user_id)
        self.memori.save_note(user_id=user_id, content=content, metadata=metadata)
        embedding = self.embed(content)
        self.milvus.upsert(user_id=user_id, content=content, embedding=embedding, metadata=metadata)

    def retrieve_context(self, user_id: str, query: str) -> MemoryContext:
        memori_profile = self.memori.query_profile(user_id)
        memori_facts = self.memori.query_recent_facts(user_id)
        memori_block = f"Profile:\n{memori_profile}\n\nRecent facts:\n{memori_facts}"

        embedding = self.embed(query or memori_facts or "")
        milvus_hits = self.milvus.search(user_id=user_id, embedding=embedding)
        stats = {
            "memori": bool(memori_profile or memori_facts),
            "milvus_hits": len(milvus_hits),
            "embedder": getattr(self.embed, "__name__", "unknown"),
        }
        return MemoryContext(
            memori_context=memori_block,
            milvus_chunks=milvus_hits,
            stats=stats,
        )

    def reset_user(self, user_id: str) -> None:
        self.memori.reset_user(user_id)
        self.milvus.drop_user(user_id)

    def health_check(self) -> Dict[str, Any]:
        return {
            "memori": True,  # would call a ping endpoint in a real client
            "milvus": self.milvus.ping(),
            "embedder": getattr(self.embed, "__name__", "unknown"),
        }
