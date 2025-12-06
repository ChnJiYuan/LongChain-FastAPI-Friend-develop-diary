from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="User/session identifier")
    message: str = Field(..., description="Latest user message")
    images: Optional[List[str]] = Field(
        default=None, description="Optional base64-encoded images"
    )


class ChatResponse(BaseModel):
    reply: str
    memori_context: Optional[str] = None
    milvus_hits: List[str] = Field(default_factory=list)
    trace_id: Optional[str] = None
