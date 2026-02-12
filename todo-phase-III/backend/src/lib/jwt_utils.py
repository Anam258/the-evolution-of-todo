from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import bcrypt
from jose import JWTError, jwt

# Get JWT secret from environment or use default
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "your-32-character-secret-key-here")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_DELTA", 1440))  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if passwords match, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """
    Generate a hash for a plain text password.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with the provided data.

    Args:
        data: Dictionary containing token claims
        expires_delta: Optional timedelta for token expiration

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token and return its claims if valid.

    Args:
        token: JWT token string to verify

    Returns:
        Dictionary containing token claims if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check if token is expired
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
            if datetime.utcnow() > exp_datetime:
                return None  # Token is expired

        return payload
    except JWTError:
        return None


def decode_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without verifying its signature.
    Use this carefully - primarily for inspection purposes.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary containing token claims if decodable, None otherwise
    """
    try:
        # This decodes without verification - use only for non-sensitive operations
        payload = jwt.get_unverified_claims(token)
        return payload
    except JWTError:
        return None


def is_token_expired(payload: Dict[str, Any]) -> bool:
    """
    Check if a JWT token is expired based on its 'exp' claim.

    Args:
        payload: Dictionary containing token claims

    Returns:
        True if token is expired, False otherwise
    """
    exp_timestamp = payload.get("exp")
    if not exp_timestamp:
        return True

    exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
    return datetime.utcnow() > exp_datetime


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract the user_id from a JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID if present and token is valid, None otherwise
    """
    payload = verify_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        user_id = payload.get("user_id")

    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except ValueError:
            return None

    return user_id