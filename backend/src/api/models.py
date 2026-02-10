from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional, Union, Dict, Any
from enum import Enum
import re


class ApiResponse(BaseModel):
    """
    Standard API response model with data and error handling.
    """
    data: Optional[Union[Dict[str, Any], list, str]] = None
    error: Optional['ApiError'] = None

    class Config:
        arbitrary_types_allowed = True


class ApiError(BaseModel):
    """
    Standard API error model.
    """
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class TokenType(str, Enum):
    """
    Enum for token types.
    """
    ACCESS = "access"
    REFRESH = "refresh"


class Token(BaseModel):
    """
    Token response model.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Token data model containing user information.
    """
    user_id: Optional[int] = None
    email: Optional[str] = None


class UserLoginRequest(BaseModel):
    """
    Request model for user login.
    """
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLoginResponse(BaseModel):
    """
    Response model for user login.
    """
    user_id: int
    email: str
    token: str


class UserRegistrationRequest(BaseModel):
    """
    Request model for user registration.
    """
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserRegistrationResponse(BaseModel):
    """
    Response model for user registration.
    """
    user_id: int
    email: str
    token: str


class UserResponse(BaseModel):
    """
    Response model for user information.
    """
    id: int
    email: str
    is_active: bool


class ErrorResponse(BaseModel):
    """
    Standard error response model.
    """
    error: ApiError


class SuccessResponse(BaseModel):
    """
    Standard success response model.
    """
    message: str
    data: Optional[Any] = None


class HealthCheckResponse(BaseModel):
    """
    Response model for health check endpoint.
    """
    status: str
    version: str
    timestamp: str


class PaginationParams(BaseModel):
    """
    Parameters for pagination.
    """
    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel):
    """
    Response model for paginated data.
    """
    data: list
    total: int
    skip: int
    limit: int