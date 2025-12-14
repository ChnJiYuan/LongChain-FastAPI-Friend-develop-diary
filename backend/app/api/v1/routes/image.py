from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.security import verify_api_key
from app.models.image import ImageRequest, ImageResponse
from app.services.vision.gemini_client import GeminiClient
from app.services.vision.sd_client import StableDiffusionClient
from app.utils.id_generator import new_trace_id

router = APIRouter()


def get_sd_client() -> StableDiffusionClient:
    return StableDiffusionClient(base_url=settings.sd_base_url, model=settings.sd_model)


def get_gemini_client() -> GeminiClient:
    return GeminiClient(
        base_url=settings.gemini_base_url,
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )


@router.get("/image/health")
async def image_health(
    sd_client: StableDiffusionClient = Depends(get_sd_client),
    gemini_client: GeminiClient = Depends(get_gemini_client),
) -> dict:
    sd_ok = settings.sd_enabled and await sd_client.health()
    gemini_ok = settings.gemini_enabled and await gemini_client.health()
    return {
        "sd_enabled": settings.sd_enabled,
        "sd_healthy": sd_ok,
        "gemini_enabled": settings.gemini_enabled,
        "gemini_healthy": gemini_ok,
    }


async def try_sd(sd_client: StableDiffusionClient, payload: ImageRequest) -> str:
    return await sd_client.txt2img(
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        steps=payload.steps,
        width=payload.width,
        height=payload.height,
    )


async def try_gemini(gemini_client: GeminiClient, payload: ImageRequest) -> str:
    return await gemini_client.generate(
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
    )


@router.post("/image", response_model=ImageResponse)
async def generate_image(
    payload: ImageRequest,
    sd_client: StableDiffusionClient = Depends(get_sd_client),
    gemini_client: GeminiClient = Depends(get_gemini_client),
    _: str | None = Depends(verify_api_key),
) -> ImageResponse:
    trace_id = new_trace_id()
    provider = (payload.provider or settings.image_provider or "auto").lower()

    if provider not in {"local", "cloud", "auto"}:
        raise HTTPException(status_code=400, detail="Invalid provider")

    # Provider priority based on requested mode
    attempts = []
    if provider == "local":
        attempts = [("local", try_sd, sd_client)]
    elif provider == "cloud":
        attempts = [("cloud", try_gemini, gemini_client)]
    else:  # auto
        attempts = [
            ("local", try_sd, sd_client),
            ("cloud", try_gemini, gemini_client),
        ]

    last_err: Exception | None = None
    for name, fn, client in attempts:
        if name == "local" and not settings.sd_enabled:
            continue
        if name == "cloud" and not (settings.gemini_enabled and settings.gemini_base_url and settings.gemini_api_key):
            continue
        try:
            img = await fn(client, payload)  # type: ignore[arg-type]
            return ImageResponse(image_base64=img, provider=name, trace_id=trace_id)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue

    raise HTTPException(status_code=502, detail=f"Image generation failed: {last_err or 'no provider available'}")
