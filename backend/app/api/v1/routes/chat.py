from fastapi import APIRouter, Depends

from app.api.v1 import deps
from app.core.security import verify_api_key
from app.models.chat import ChatRequest, ChatResponse
from app.services.chains.chat_chain import ChatChain

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a chat message",
    response_description="Assistant reply plus retrieved Memori/Milvus context.",
    description=(
        "Accepts a user message (and optional base64 images) to run the chat chain. "
        "Returns the assistant reply, Memori structured context, Milvus semantic hits, "
        "and a trace id for log correlation. Request fields are trimmed and validated."
    ),
)
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
        milvus_chunks=result.milvus_chunks,
        trace_id=result.trace_id,
    )
