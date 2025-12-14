import logging
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


class GeminiClient:
    """Simple Gemini/Banana nano image generation client."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def health(self) -> bool:
        if not self.base_url or not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(self.base_url)
                return resp.status_code < 500
        except Exception as exc:
            logger.warning("Gemini health failed: %s", exc)
            return False

    async def generate(self, prompt: str, negative_prompt: str | None = None) -> str:
        if not self.base_url or not self.api_key:
            raise RuntimeError("Gemini is not configured")
        payload: Dict[str, Any] = {"prompt": prompt, "model": self.model}
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self.base_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # Try common fields
            for key in ("image_base64", "base64_image", "image"):
                val = data.get(key)
                if isinstance(val, str) and val:
                    return val
            # Some APIs return list in 'images' or 'output'
            for key in ("images", "output"):
                val = data.get(key)
                if isinstance(val, list) and val and isinstance(val[0], str):
                    return val[0]
            raise RuntimeError("No image found in Gemini response")
