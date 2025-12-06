from typing import Optional

from app.services.llm.ollama_client import OllamaClient
from app.services.llm.openai_client import OpenAIClient


class LLMRouter:
    """Tiny router deciding which LLM backend to call."""

    def __init__(
        self,
        default_provider: str,
        openai_client: OpenAIClient,
        ollama_client: OllamaClient,
    ) -> None:
        self.default_provider = default_provider
        self.openai = openai_client
        self.ollama = ollama_client

    async def generate(self, prompt: str, provider: Optional[str] = None) -> str:
        choice = (provider or self.default_provider).lower()
        if choice == "ollama":
            return await self.ollama.generate(prompt)
        if choice == "mock":
            return "[mock llm reply]"
        return await self.openai.generate(prompt)
