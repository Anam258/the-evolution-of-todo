from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional, Dict, Any
from src.lib.jwt_utils import verify_token, get_user_id_from_token

security = HTTPBearer()

PUBLIC_PATHS = frozenset({
    "/", "/health", "/monitoring/health", "/monitoring/metrics",
    "/auth/register", "/auth/login", "/auth/logout", "/auth/health",
    "/docs", "/redoc", "/openapi.json",
})


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Class-based ASGI middleware that extracts JWT claims into request.state
    on every request.  Public paths get user_id=None; protected paths with
    a bad/missing token are rejected here so route handlers never have to
    worry about it.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Always allow OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path.rstrip("/")
        is_public = path in PUBLIC_PATHS or path.startswith("/auth/")

        auth_header = request.headers.get("authorization", "")
        request.state.user_id = None
        request.state.token_payload = None

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if self._is_valid_format(token):
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("user_id") or payload.get("sub")
                    if isinstance(user_id, str):
                        try:
                            user_id = int(user_id)
                        except ValueError:
                            user_id = None
                    request.state.user_id = user_id
                    request.state.token_payload = payload

        # If a protected path has no valid user, reject early
        if not is_public and request.state.user_id is None:
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid authentication token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)

    @staticmethod
    def _is_valid_format(token: str) -> bool:
        return token.count(".") == 2


# ---------------------------------------------------------------------------
# Dependency-injection helpers (used by route handlers via Depends)
# ---------------------------------------------------------------------------

def get_current_user_id(request: Request) -> int:
    """Extract user_id that the middleware already validated."""
    uid = getattr(request.state, "user_id", None)
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return uid


def require_authenticated_user():
    """FastAPI Depends() wrapper returning the authenticated user_id."""
    def _dep(request: Request) -> int:
        return get_current_user_id(request)
    return _dep
