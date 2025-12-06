from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class MemoryWriteRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class MemoryQuery(BaseModel):
    query: str
    top_k: int = 5


class MemoryDebugResponse(BaseModel):
    user_id: str
    memori: str
    milvus: List[str]
    stats: Dict[str, Any]
