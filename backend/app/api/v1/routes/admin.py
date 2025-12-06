from fastapi import APIRouter, Depends

from app.api.v1 import deps
from app.core.security import verify_api_key
from app.services.memory.memory_service import MemoryService

router = APIRouter()


@router.post("/admin/reset/{user_id}")
async def reset_user(
    user_id: str,
    memory_service: MemoryService = Depends(deps.get_memory_service),
    _: str | None = Depends(verify_api_key),
) -> dict:
    memory_service.reset_user(user_id)
    return {"status": "reset", "user_id": user_id}


@router.get("/admin/health")
async def admin_health(
    memory_service: MemoryService = Depends(deps.get_memory_service),
    _: str | None = Depends(verify_api_key),
) -> dict:
    return memory_service.health_check()
