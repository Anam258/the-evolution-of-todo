from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from typing import Dict, Any
from ..database import get_session
from ..services.auth_service import auth_service
from ..api.models import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegistrationRequest,
    UserRegistrationResponse,
    ApiResponse,
    ApiError
)
from ..middleware.auth_middleware import get_current_user_id
from ..models.user import User
from ..utils.rate_limiter import auth_rate_limiter, get_client_ip, get_rate_limit_key

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=ApiResponse)
def register(request: Request, user_data: UserRegistrationRequest, db_session: Session = Depends(get_session)):
    """
    Register a new user.

    Args:
        request: FastAPI request object
        user_data: User registration information
        db_session: Database session

    Returns:
        ApiResponse with user information and token
    """
    # Rate limiting for registration
    client_ip = get_client_ip(request)
    rate_limit_key = get_rate_limit_key(client_ip, "/auth/register")

    is_allowed, reset_time = auth_rate_limiter.is_registration_allowed(rate_limit_key)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later.",
            headers=auth_rate_limiter.get_rate_limit_headers(False, reset_time)
        )

    # Check if user already exists
    existing_user = auth_service.get_user_by_email(db_session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Create new user
    from ..models.user import UserCreate
    user_create = UserCreate(email=user_data.email, password=user_data.password)
    db_user = auth_service.create_user(db_session, user_create)

    # Create access token
    token = auth_service.create_access_token_for_user(db_user)

    return ApiResponse(
        data=UserRegistrationResponse(
            user_id=db_user.id,
            email=db_user.email,
            token=token
        ).dict()
    )


@router.post("/login", response_model=ApiResponse)
def login(request: Request, user_data: UserLoginRequest, db_session: Session = Depends(get_session)):
    """
    Authenticate user and return access token.

    Args:
        request: FastAPI request object
        user_data: User login credentials
        db_session: Database session

    Returns:
        ApiResponse with user information and token
    """
    # Rate limiting for login attempts
    client_ip = get_client_ip(request)
    rate_limit_key = get_rate_limit_key(client_ip, "/auth/login")

    is_allowed, reset_time = auth_rate_limiter.is_login_allowed(rate_limit_key)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers=auth_rate_limiter.get_rate_limit_headers(False, reset_time)
        )

    user = auth_service.authenticate_user(
        db_session, user_data.email, user_data.password
    )

    if not user:
        # Log failed authentication attempt for security monitoring
        from ..utils.logger import log_authentication_event
        log_authentication_event(
            event_type="login_failure",
            user_identifier=user_data.email,
            success=False,
            ip_address=client_ip
        )

        # Still rate limit even on failed login attempts
        # Update rate limit counter
        auth_rate_limiter.login_attempts_limiter.is_allowed(
            rate_limit_key,
            auth_rate_limiter.LOGIN_ATTEMPTS_LIMIT,
            auth_rate_limiter.LOGIN_WINDOW_SIZE
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log successful authentication
    from ..utils.logger import log_authentication_event
    log_authentication_event(
        event_type="login_success",
        user_identifier=user_data.email,
        success=True,
        ip_address=client_ip
    )

    # Create access token
    token = auth_service.create_access_token_for_user(user)

    return ApiResponse(
        data=UserLoginResponse(
            user_id=user.id,
            email=user.email,
            token=token
        ).dict()
    )


@router.post("/logout")
def logout():
    """
    Logout user (client-side token removal is sufficient for JWT).

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=ApiResponse)
def get_current_user(
    request: Request,
    db_session: Session = Depends(get_session),
):
    """
    Get current authenticated user's information.

    Args:
        request: FastAPI request object
        db_session: Database session

    Returns:
        ApiResponse with user information
    """
    current_user_id = get_current_user_id(request)
    user = auth_service.get_user_by_id(db_session, current_user_id)

    if not user:
        # This shouldn't happen if the token is valid, but just in case
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ApiResponse(
        data={
            "user_id": user.id,
            "email": user.email
        }
    )


@router.get("/{user_id}", response_model=ApiResponse)
def get_user_by_id(
    user_id: int,
    request: Request,
    db_session: Session = Depends(get_session),
):
    """
    Get a specific user's public information.
    NOTE: This endpoint demonstrates the 404 vs 403 principle.
    If the requested user doesn't exist OR doesn't belong to the authenticated user,
    we return 404 to prevent enumeration attacks.

    Args:
        user_id: ID of the user to retrieve
        current_user_id: ID of the authenticated user
        db_session: Database session

    Returns:
        ApiResponse with user information
    """
    current_user_id = get_current_user_id(request)
    if current_user_id != user_id:
        # Return 404 instead of 403 to prevent enumeration attacks
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user = auth_service.get_user_by_id(db_session, user_id)

    if not user:
        # User doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ApiResponse(
        data={
            "user_id": user.id,
            "email": user.email
        }
    )


@router.get("/health")
def health_check():
    """
    Health check endpoint for the authentication service.

    Returns:
        Health status
    """
    return {"status": "ok", "service": "auth"}