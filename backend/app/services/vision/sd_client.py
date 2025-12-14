import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class StableDiffusionClient:
    """Client for local Stable Diffusion WebUI (txt2img)."""

    def __init__(self, base_url: str, model: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model or ""

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/sdapi/v1/sd-models")
                resp.raise_for_status()
            return True
        except Exception as exc:
            logger.warning("SD health check failed: %s", exc)
            return False

    async def txt2img(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        steps: int = 20,
        width: int = 512,
        height: int = 512,
    ) -> str:
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "steps": steps,
            "width": width,
            "height": height,
        }
        if self.model:
            payload["override_settings"] = {"sd_model_checkpoint": self.model}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/sdapi/v1/txt2img", json=payload)
            resp.raise_for_status()
            data = resp.json()
            images = data.get("images") or []
            if not images:
                raise RuntimeError("No image returned from Stable Diffusion")
            return images[0]
