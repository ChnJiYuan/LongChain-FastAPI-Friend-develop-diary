from dataclasses import dataclass
from typing import List, Optional

from app.services.llm.prompts import SYSTEM_PROMPT, build_chat_prompt
from app.services.llm.router import LLMRouter
from app.services.memory.memory_service import MemoryService
from app.utils.id_generator import new_trace_id


@dataclass
class ChatResult:
    reply: str
    memori_context: str
    milvus_chunks: List[str]
    trace_id: str


class ChatChain:
    """Main chat orchestration chain."""

    def __init__(self, memory_service: MemoryService, llm_router: LLMRouter) -> None:
        self.memory_service = memory_service
        self.llm_router = llm_router

    async def run(self, user_id: str, message: str, images: Optional[List[str]] = None) -> ChatResult:
        context = self.memory_service.retrieve_context(user_id=user_id, query=message)
        prompt = build_chat_prompt(
            system_prompt=SYSTEM_PROMPT,
            memori_context=context.memori_context,
            milvus_chunks=context.milvus_chunks,
            user_message=message,
        )
        reply = await self.llm_router.generate(prompt)
        return ChatResult(
            reply=reply,
            memori_context=context.memori_context,
            milvus_chunks=context.milvus_chunks,
            trace_id=new_trace_id(),
        )
