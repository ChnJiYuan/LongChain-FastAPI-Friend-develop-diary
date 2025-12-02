from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    # Placeholder: wire to backend.chains.conversation
    return ChatResponse(reply=f"Echo: {req.message}")
