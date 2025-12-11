from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    user_id: str = Field(
        ...,
        description="User/session identifier (trimmed)",
        min_length=1,
        max_length=128,
    )
    message: str = Field(
        ...,
        description="Latest user message (plain text)",
        min_length=1,
        max_length=4000,
    )
    images: Optional[List[str]] = Field(
        default=None,
        description="Optional base64-encoded images (data URI allowed)",
        max_length=5,
    )

    @field_validator("user_id", "message")
    @classmethod
    def not_blank(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("images")
    @classmethod
    def validate_images(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return None
        cleaned = []
        for img in v:
            if not img or not img.strip():
                raise ValueError("images cannot contain empty strings")
            cleaned.append(img.strip())
        return cleaned


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Assistant reply text")
    memori_context: Optional[str] = Field(
        default=None, description="Structured context fetched from Memori"
    )
    milvus_chunks: List[str] = Field(
        default_factory=list, description="Top semantic hits from Milvus"
    )
    trace_id: Optional[str] = Field(
        default=None, description="Trace identifier for correlating backend logs"
    )
