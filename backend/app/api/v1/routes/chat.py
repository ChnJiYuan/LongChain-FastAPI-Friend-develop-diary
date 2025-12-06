from fastapi import APIRouter, Depends

from app.api.v1 import deps
from app.core.security import verify_api_key
from app.models.chat import ChatRequest, ChatResponse
from app.services.chains.chat_chain import ChatChain

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    chain: ChatChain = Depends(deps.get_chat_chain),
    _: str | None = Depends(verify_api_key),
) -> ChatResponse:
    result = await chain.run(
        user_id=payload.user_id,
        message=payload.message,
        images=payload.images,
    )
    return ChatResponse(
        reply=result.reply,
        memori_context=result.memori_context,
        milvus_hits=result.milvus_hits,
        trace_id=result.trace_id,
    )
