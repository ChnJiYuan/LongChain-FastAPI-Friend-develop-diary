import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class OllamaClient:
    """Simple Ollama HTTP wrapper."""

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,  # return a single JSON object
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content: Optional[str] = data.get("response")
                return content or ""
        except Exception as exc:  # pragma: no cover - depends on running Ollama
            logger.warning("Ollama request failed: %s", exc)
            return "[ollama placeholder reply]"
