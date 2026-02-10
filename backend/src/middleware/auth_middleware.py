from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from functools import wraps
from src.lib.jwt_utils import verify_token, get_user_id_from_token
import os

# Initialize security scheme
security = HTTPBearer()

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT token from Authorization header and return its payload.

    Args:
        credentials: HTTP Authorization credentials from header

    Returns:
        Token payload if valid

    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials

    # Check if token is empty or None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def verify_jwt_token_or_none(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token from Authorization header and return its payload if valid, None otherwise.

    Args:
        credentials: HTTP Authorization credentials from header

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        token = credentials.credentials

        if not token:
            return None

        payload = verify_token(token)

        if payload is None:
            return None

        return payload
    except HTTPException:
        # If there's an HTTP exception (like missing header), return None
        return None


def verify_jwt_in_request(request) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token from Authorization header in request object.

    Args:
        request: FastAPI request object

    Returns:
        Token payload if valid, None otherwise
    """
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header[len("Bearer "):]
    payload = verify_token(token)

    return payload


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Extract user_id from JWT token in Authorization header.

    Args:
        credentials: HTTP Authorization credentials from header

    Returns:
        User ID if token is valid

    Raises:
        HTTPException: If token is invalid, missing, or user_id not found
    """
    token = credentials.credentials
    user_id = get_user_id_from_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def require_auth():
    """
    Decorator to require authentication for a route.
    Returns the authenticated user's ID.
    """
    def auth_dependency(current_user_id: int = Depends(get_current_user_id)):
        return current_user_id
    return auth_dependency


def verify_secret_key():
    """
    Verify that the JWT secret key is properly configured.

    Raises:
        ValueError: If JWT secret is missing or too short
    """
    secret = os.getenv("BETTER_AUTH_SECRET")

    if not secret:
        raise ValueError("BETTER_AUTH_SECRET environment variable not set")

    if len(secret) < 32:
        raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters long")


def verify_token_format(token: str) -> bool:
    """
    Verify the basic format of a JWT token (has 3 parts separated by dots).

    Args:
        token: JWT token string

    Returns:
        True if format is valid, False otherwise
    """
    parts = token.split(".")
    return len(parts) == 3


async def auth_middleware(request, call_next):
    """
    ASGI middleware to add authentication context to requests.
    This middleware can be added to FastAPI applications to provide
    authentication information to all routes.
    """
    # Check for authorization header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]

        # Verify token format
        if verify_token_format(token):
            # Attempt to get user ID from token
            user_id = get_user_id_from_token(token)
            # Add to request state for use in route handlers
            request.state.user_id = user_id
        else:
            request.state.user_id = None
    else:
        request.state.user_id = None

    response = await call_next(request)
    return response


def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[int]:
    """
    Get current user ID if authenticated, or None if not.
    Used for routes that work for both authenticated and unauthenticated users.
    """
    try:
        token = credentials.credentials
        user_id = get_user_id_from_token(token)
        return user_id
    except HTTPException:
        return None


def require_authenticated_user():
    """
    Decorator to require authentication for a route.
    Returns the authenticated user's ID.

    Example usage:
    @app.get("/protected")
    def protected_route(current_user_id: int = Depends(require_authenticated_user())):
        return {"user_id": current_user_id}
    """
    def auth_dependency(current_user_id: int = Depends(get_current_user_id)):
        return current_user_id
    return auth_dependency


def require_valid_token():
    """
    Decorator to require a valid token for a route.
    Returns the token payload.
    """
    def token_dependency(token_data: Dict[str, Any] = Depends(verify_jwt_token)):
        return token_data
    return token_dependency