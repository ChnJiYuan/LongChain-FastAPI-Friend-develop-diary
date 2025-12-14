from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.security import verify_api_key
from app.models.image import ImageRequest, ImageResponse
from app.services.vision.sd_client import StableDiffusionClient
from app.utils.id_generator import new_trace_id

router = APIRouter()


def get_sd_client() -> StableDiffusionClient:
    return StableDiffusionClient(base_url=settings.sd_base_url, model=settings.sd_model)


@router.get("/image/health")
async def image_health(sd_client: StableDiffusionClient = Depends(get_sd_client)) -> dict:
    healthy = settings.sd_enabled and await sd_client.health()
    return {"sd_enabled": settings.sd_enabled, "sd_healthy": healthy}


@router.post("/image", response_model=ImageResponse)
async def generate_image(
    payload: ImageRequest,
    sd_client: StableDiffusionClient = Depends(get_sd_client),
    _: str | None = Depends(verify_api_key),
) -> ImageResponse:
    trace_id = new_trace_id()
    provider = (payload.provider or settings.image_provider or "auto").lower()

    if provider not in {"local", "cloud", "auto"}:
        raise HTTPException(status_code=400, detail="Invalid provider")

    if not settings.sd_enabled and provider in {"local", "auto"}:
        raise HTTPException(status_code=503, detail="Local SD disabled")

    # Only local implemented; cloud/Gemini would be added here later.
    try:
        image_b64 = await sd_client.txt2img(
            prompt=payload.prompt,
            negative_prompt=payload.negative_prompt,
            steps=payload.steps,
            width=payload.width,
            height=payload.height,
        )
        return ImageResponse(image_base64=image_b64, provider="local", trace_id=trace_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Stable Diffusion failed: {exc}") from exc
