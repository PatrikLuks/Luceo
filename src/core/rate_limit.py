"""Rate limiting configuration using slowapi (in-memory, Redis-swappable)."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from src.core.security import decode_access_token


def _key_func(request: Request) -> str:
    """Extract user_id from JWT if present, otherwise fall back to IP."""
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            pass
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(key_func=_key_func)
