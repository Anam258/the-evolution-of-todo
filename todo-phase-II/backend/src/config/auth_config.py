"""
Authentication configuration for the backend application.
This module handles the validation and configuration of authentication settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class AuthConfig:
    """
    Configuration class for authentication settings.
    """

    def __init__(self):
        self.secret_key: str = self._validate_secret_key()
        self.algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(os.getenv("JWT_EXPIRATION_DELTA", 1440))  # 24 hours

    def _validate_secret_key(self) -> str:
        """
        Validate that the JWT secret key is properly configured.

        Returns:
            The secret key if valid

        Raises:
            ValueError: If JWT secret is missing or too short
        """
        secret = os.getenv("BETTER_AUTH_SECRET")

        # Log environment variable access attempt
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        if secret:
            logger.info("BETTER_AUTH_SECRET environment variable loaded successfully")
        else:
            logger.warning("BETTER_AUTH_SECRET environment variable not found")

        if not secret:
            logger.error("BETTER_AUTH_SECRET environment variable not set")
            raise ValueError(
                "BETTER_AUTH_SECRET environment variable not set. "
                "Set it in your .env file (local dev) or platform environment variables (production)."
            )

        if len(secret) < 32:
            logger.error(f"BETTER_AUTH_SECRET is too short: {len(secret)} characters, need at least 32")
            raise ValueError(f"BETTER_AUTH_SECRET must be at least 32 characters long. "
                           f"Current length: {len(secret)} characters.")
        else:
            logger.info(f"BETTER_AUTH_SECRET validation passed: {len(secret)} characters")

        return secret

    def get_secret_key(self) -> str:
        """
        Get the configured secret key.

        Returns:
            The secret key
        """
        return self.secret_key

    def is_valid_secret_key(self) -> bool:
        """
        Check if the secret key is validly configured.

        Returns:
            True if valid, False otherwise
        """
        try:
            self._validate_secret_key()
            return True
        except ValueError:
            return False


# Global instance for convenience
auth_config = AuthConfig()


def verify_shared_secret_configuration() -> tuple[bool, str]:
    """
    Verify that the shared secret is properly configured for cross-service validation.

    Returns:
        Tuple of (is_valid, error_message) where is_valid indicates if configuration is valid
        and error_message provides details if not valid
    """
    try:
        # This would check that both frontend and backend can access the same secret
        # In a real implementation, this might involve checking that the secret
        # can be used to both encode and decode tokens successfully
        secret = auth_config.get_secret_key()

        # Perform a basic validation that the secret is not empty and has proper length
        if not secret:
            return False, "JWT_SECRET is not set or empty"

        if len(secret) < 32:
            return False, f"JWT_SECRET is too short (minimum 32 characters), current length: {len(secret)}"

        # Additional checks could be performed here in a real implementation
        # such as attempting to encode/decode a test token to ensure cross-service compatibility
        return True, ""
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error during secret validation: {str(e)}"


def test_cross_service_compatibility() -> tuple[bool, str]:
    """
    Test that tokens generated with this secret can be properly verified,
    simulating cross-service compatibility.

    Returns:
        Tuple of (is_compatible, message) indicating compatibility status
    """
    try:
        from ..lib.jwt_utils import create_access_token, verify_token

        # Create a test token
        test_data = {"sub": "test", "user_id": 123}
        test_token = create_access_token(test_data)

        # Try to verify the token
        result = verify_token(test_token)

        if result is None:
            return False, "Failed to verify a token created with the current secret - possible secret mismatch"

        if result.get("sub") != "test":
            return False, "Token verification succeeded but payload was altered - possible secret mismatch"

        return True, "Cross-service token verification successful"

    except Exception as e:
        return False, f"Error during cross-service compatibility test: {str(e)}"


def validate_startup_configuration() -> None:
    """
    Validate all required authentication configurations at startup.

    Raises:
        ValueError: If any required configuration is missing or invalid
    """
    # Validate the secret key
    auth_config._validate_secret_key()

    # Add other validation checks as needed
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    if algorithm not in ["HS256", "HS384", "HS512"]:
        raise ValueError(f"Unsupported JWT algorithm: {algorithm}")

    expiration = os.getenv("JWT_EXPIRATION_DELTA")
    if expiration:
        try:
            exp_value = int(expiration)
            if exp_value <= 0:
                raise ValueError("JWT_EXPIRATION_DELTA must be a positive integer")
        except ValueError:
            raise ValueError("JWT_EXPIRATION_DELTA must be a valid integer")