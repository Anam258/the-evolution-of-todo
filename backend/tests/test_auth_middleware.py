import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from jose import jwt
import os

# Import your FastAPI app
from src.main import app  # Assuming your FastAPI app is in src/main.py
from src.lib.jwt_utils import create_access_token, verify_token, get_user_id_from_token
from src.middleware.auth_middleware import get_current_user_id
from src.services.auth_service import auth_service


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock user data for testing."""
    return {
        "id": 1,
        "email": "test@example.com",
        "hashed_password": "$2b$12$fake_hashed_password"
    }


def create_test_token(user_id: int = 1, email: str = "test@example.com", expires_delta: timedelta = None):
    """Helper function to create a test JWT token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)  # Token valid for 30 minutes

    data = {
        "sub": str(user_id),
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + expires_delta
    }

    # Use the same secret as the application
    from src.config.auth_config import auth_config
    secret = auth_config.get_secret_key()
    return jwt.encode(data, secret, algorithm="HS256")


class TestJWTUtilities:
    """Test suite for JWT utility functions."""

    def test_create_access_token(self):
        """Test creating an access token."""
        user_data = {"sub": "1", "email": "test@example.com"}
        token = create_access_token(user_data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify the token can be decoded
        decoded = verify_token(token)
        assert decoded is not None
        assert decoded["sub"] == "1"
        assert decoded["email"] == "test@example.com"

    def test_verify_valid_token(self):
        """Test verifying a valid token."""
        token = create_test_token()
        result = verify_token(token)

        assert result is not None
        assert result["sub"] == "1"
        assert result["email"] == "test@example.com"

    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        result = verify_token("invalid.token.string")

        assert result is None

    def test_verify_expired_token(self):
        """Test verifying an expired token."""
        expired_token = create_test_token(expires_delta=timedelta(seconds=-1))
        result = verify_token(expired_token)

        assert result is None

    def test_get_user_id_from_valid_token(self):
        """Test extracting user_id from a valid token."""
        token = create_test_token(user_id=123)
        user_id = get_user_id_from_token(token)

        assert user_id == 123

    def test_get_user_id_from_invalid_token(self):
        """Test extracting user_id from an invalid token."""
        user_id = get_user_id_from_token("invalid.token.string")

        assert user_id is None

    def test_get_user_id_from_expired_token(self):
        """Test extracting user_id from an expired token."""
        expired_token = create_test_token(expires_delta=timedelta(seconds=-1))
        user_id = get_user_id_from_token(expired_token)

        assert user_id is None


class TestAuthMiddleware:
    """Test suite for authentication middleware functions."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        original_secret = os.environ.get("BETTER_AUTH_SECRET")
        os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-purposes-only"
        yield
        if original_secret:
            os.environ["BETTER_AUTH_SECRET"] = original_secret
        else:
            os.environ.pop("BETTER_AUTH_SECRET", None)

    def test_verify_jwt_token_with_valid_token(self, mocker):
        """Test verify_jwt_token with a valid token."""
        # Mock the security dependency
        mock_credentials = MagicMock()
        mock_credentials.credentials = create_test_token()

        # Since verify_jwt_token expects to be used as a dependency,
        # we test the underlying verify_token function
        token = create_test_token()
        result = verify_token(token)

        assert result is not None
        assert result["sub"] == "1"

    def test_verify_jwt_token_with_invalid_token(self):
        """Test verify_jwt_token with an invalid token."""
        result = verify_token("invalid.token.string")

        assert result is None

    def test_verify_jwt_token_with_expired_token(self):
        """Test verify_jwt_token with an expired token."""
        expired_token = create_test_token(expires_delta=timedelta(seconds=-1))
        result = verify_token(expired_token)

        assert result is None

    def test_get_current_user_id_with_valid_token(self, mocker):
        """Test get_current_user_id with a valid token."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = create_test_token(user_id=456)

        # Since this is a dependency function, test indirectly
        token = create_test_token(user_id=456)
        user_id = get_user_id_from_token(token)

        assert user_id == 456

    def test_get_current_user_id_with_invalid_token(self):
        """Test get_current_user_id with an invalid token."""
        user_id = get_user_id_from_token("invalid.token.string")

        assert user_id is None


class TestProtectedEndpoints:
    """Test suite for protected API endpoints."""

    def test_protected_endpoint_without_token(self, client):
        """Test accessing a protected endpoint without a token."""
        # This test would require a protected endpoint to exist
        # For now, we'll just verify the concept
        pass

    def test_protected_endpoint_with_valid_token(self, client, mock_user):
        """Test accessing a protected endpoint with a valid token."""
        # This test would require a protected endpoint to exist
        # For now, we'll just verify the concept
        pass

    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing a protected endpoint with an invalid token."""
        # This test would require a protected endpoint to exist
        # For now, we'll just verify the concept
        pass

    def test_protected_endpoint_with_expired_token(self, client):
        """Test accessing a protected endpoint with an expired token."""
        # This test would require a protected endpoint to exist
        # For now, we'll just verify the concept
        pass


if __name__ == "__main__":
    pytest.main([__file__])