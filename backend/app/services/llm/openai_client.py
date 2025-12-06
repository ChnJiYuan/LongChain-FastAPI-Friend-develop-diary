import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore


class OpenAIClient:
    """Minimal OpenAI chat wrapper with a graceful fallback when SDK is absent."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set; returning placeholder answer")
            return "[openai placeholder reply]"

        if OpenAI is None:
            logger.warning("openai SDK not installed; returning placeholder answer")
            return "[openai placeholder reply]"

        client = OpenAI(api_key=self.api_key)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        content: Optional[str] = resp.choices[0].message.content
        return content or ""
