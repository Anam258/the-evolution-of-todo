from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional, Dict, Any
from lib.jwt_utils import verify_token, get_user_id_from_token

security = HTTPBearer()

# Exact paths that never require a JWT (infrastructure / docs)
PUBLIC_PATHS = frozenset({
    "/", "/health", "/monitoring/health", "/monitoring/metrics",
    "/docs", "/redoc", "/openapi.json",
})

# Auth routes that are open (no token needed).
# /auth/me and /auth/{user_id} are intentionally EXCLUDED — they need JWT.
PUBLIC_AUTH_PATHS = frozenset({
    "/auth/register",
    "/auth/login",
    "/auth/logout",
    "/auth/health",
    "/auth/callback",
})


# Known API version prefixes to strip before matching
_API_PREFIXES = ("/api/v1",)


def _is_public(path: str) -> bool:
    """Return True if this path should skip JWT verification entirely."""
    if path in PUBLIC_PATHS:
        return True
    # Strip version prefix so /api/v1/auth/register matches /auth/register
    normalized = path
    for prefix in _API_PREFIXES:
        if path.startswith(prefix):
            normalized = path[len(prefix):]
            break
    return normalized in PUBLIC_AUTH_PATHS


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Class-based ASGI middleware that extracts JWT claims into request.state
    on every request.  Public paths are passed straight through without
    even inspecting the Authorization header.  Protected paths with a
    bad/missing token are rejected before the route handler runs.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        raw = request.url.path
        path = raw.rstrip("/") or "/"     # "/" must stay as "/"

        # ── Debug: show every path the middleware sees ────────────────
        print(f"[AUTH-MW] Checking path: {request.method} {raw}  (normalized: {path})")

        # Always allow OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            print(f"[AUTH-MW] -> OPTIONS preflight, passing through")
            return await call_next(request)

        # ── Public route? Pass immediately — don't touch headers ─────
        if _is_public(path):
            print(f"[AUTH-MW] -> PUBLIC route, skipping JWT check")
            request.state.user_id = None
            request.state.token_payload = None
            return await call_next(request)

        # ── Protected route: extract & validate JWT ──────────────────
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

        if request.state.user_id is None:
            print(f"[AUTH-MW] -> PROTECTED route, NO valid token — returning 401")
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid authentication token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        print(f"[AUTH-MW] -> PROTECTED route, user_id={request.state.user_id} — OK")
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
