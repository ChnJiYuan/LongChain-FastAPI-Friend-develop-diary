from fastapi import APIRouter

router = APIRouter()


@router.post("/invoke")
async def invoke_agent(payload: dict):
    # Placeholder: route to backend.chains.agent for tool execution
    return {"tools": [], "input": payload, "status": "not_implemented"}
