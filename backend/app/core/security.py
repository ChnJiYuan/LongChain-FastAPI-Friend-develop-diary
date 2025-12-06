from fastapi import Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Depends(api_key_header)) -> str | None:
    """Optional API key guard; if no key is set in env, allow all traffic."""
    configured_key = settings.memori_api_key  # reuse memori key slot if desired
    if not configured_key:
        return None
    if api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key


__all__ = ["verify_api_key"]
