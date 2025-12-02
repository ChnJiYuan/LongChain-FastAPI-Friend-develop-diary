from fastapi import APIRouter
from pydantic import BaseModel

from backend.config import settings

router = APIRouter()


class ImageGenRequest(BaseModel):
    prompt: str
    steps: int = 20


@router.post("/image")
async def generate_image(req: ImageGenRequest):
    # Placeholder: call gpu_inference.sd_generator using settings.sd_model_dir
    return {
        "prompt": req.prompt,
        "steps": req.steps,
        "model_dir": settings.sd_model_dir,
        "status": "queued",
    }
