from fastapi import APIRouter, Depends, Query

from app.api.v1 import deps
from app.core.security import verify_api_key
from app.models.memory import MemoryDebugResponse, MemoryQuery, MemoryWriteRequest
from app.services.memory.memory_service import MemoryService

router = APIRouter()


@router.get("/memory/{user_id}", response_model=MemoryDebugResponse)
async def get_memory_snapshot(
    user_id: str,
    q: str | None = Query(None, alias="query"),
    memory_service: MemoryService = Depends(deps.get_memory_service),
    _: str | None = Depends(verify_api_key),
) -> MemoryDebugResponse:
    context = memory_service.retrieve_context(user_id=user_id, query=q or "")
    return MemoryDebugResponse(
        user_id=user_id,
        memori=context.memori_context,
        milvus=context.milvus_chunks,
        stats=context.stats,
    )


@router.post("/memory/{user_id}")
async def write_memory(
    user_id: str,
    payload: MemoryWriteRequest,
    memory_service: MemoryService = Depends(deps.get_memory_service),
    _: str | None = Depends(verify_api_key),
) -> dict:
    memory_service.record_user_message(
        user_id=user_id, content=payload.content, metadata=payload.metadata
    )
    return {"status": "ok"}
