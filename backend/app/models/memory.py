from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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


class MemoryHealthResponse(BaseModel):
    memori: bool = Field(..., description="Whether Memori client is available")
    milvus: bool = Field(..., description="Whether Milvus client is reachable or fallback is active")
    embedder: str = Field(..., description="Identifier for the embedder in use")
