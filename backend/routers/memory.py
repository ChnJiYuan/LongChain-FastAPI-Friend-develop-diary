from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class MemoryItem(BaseModel):
    key: str
    value: str


@router.get("/{user_id}")
async def get_memory(user_id: str):
    return {"user_id": user_id, "memories": []}


@router.post("/{user_id}")
async def upsert_memory(user_id: str, item: MemoryItem):
    # Placeholder: write to vector store / JSON profile
    return {"status": "saved", "user_id": user_id, "item": item}
