"""
Integration tests for token expiry handling.
Tests that expired tokens are properly rejected.
"""

import pytest
import os
import time
from datetime import datetime, timedelta
from jose import jwt
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestTokenExpiry:
    """Test suite for token expiration handling."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        self.original_secret = os.environ.get("BETTER_AUTH_SECRET")
        self.original_database_url = os.environ.get("DATABASE_URL")

        os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-purposes-only"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"

        yield

        if self.original_secret:
            os.environ["BETTER_AUTH_SECRET"] = self.original_secret
        else:
            os.environ.pop("BETTER_AUTH_SECRET", None)

        if self.original_database_url:
            os.environ["DATABASE_URL"] = self.original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

    @pytest.fixture
    def mock_user(self):
        """Create a mock user object."""
        from src.models.user import User
        mock = MagicMock(spec=User)
        mock.id = 1
        mock.email = "test@example.com"
        mock.hashed_password = "$2b$12$test_hashed_password"
        mock.is_active = True
        return mock

    def create_expired_token(self, user_id: int = 1, email: str = "test@example.com", expired_seconds_ago: int = 60):
        """Create a JWT token that is already expired."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        exp_time = int(time.time()) - expired_seconds_ago

        payload = {
            "sub": str(user_id),
            "user_id": user_id,
            "email": email,
            "iat": int(time.time()) - (expired_seconds_ago + 3600),  # Issued 1 hour before expiry
            "exp": exp_time
        }

        return jwt.encode(payload, secret, algorithm="HS256")

    def create_valid_token(self, user_id: int = 1, email: str = "test@example.com", expires_in_seconds: int = 3600):
        """Create a valid JWT token."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        payload = {
            "sub": str(user_id),
            "user_id": user_id,
            "email": email,
            "iat": current_time,
            "exp": current_time + expires_in_seconds
        }

        return jwt.encode(payload, secret, algorithm="HS256")

    def test_expired_token_returns_401(self):
        """Test that expired tokens return 401 Unauthorized."""
        expired_token = self.create_expired_token(expired_seconds_ago=60)

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Should return 401
        assert response.status_code == 401

    def test_freshly_expired_token_returns_401(self):
        """Test that tokens that just expired return 401."""
        # Create a token that expired 1 second ago
        expired_token = self.create_expired_token(expired_seconds_ago=1)

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Should return 401
        assert response.status_code == 401

    def test_old_expired_token_returns_401(self):
        """Test that old expired tokens return 401."""
        # Create a token that expired 24 hours ago
        expired_token = self.create_expired_token(expired_seconds_ago=86400)

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Should return 401
        assert response.status_code == 401

    def test_valid_token_is_accepted(self, mock_user):
        """Test that valid non-expired tokens are accepted."""
        valid_token = self.create_valid_token()
        mock_db_session = MagicMock()

        with patch('src.database.get_session', return_value=mock_db_session):
            with patch('src.services.auth_service.auth_service.get_user_by_id', return_value=mock_user):
                from src.main import app
                client = TestClient(app)

                response = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {valid_token}"}
                )

                # Should return 200
                assert response.status_code == 200
                assert response.json()["data"]["email"] == "test@example.com"

    def test_token_near_expiry_is_still_valid(self, mock_user):
        """Test that tokens near expiry (but not expired) are still valid."""
        # Create a token that expires in 5 seconds
        token = self.create_valid_token(expires_in_seconds=5)
        mock_db_session = MagicMock()

        with patch('src.database.get_session', return_value=mock_db_session):
            with patch('src.services.auth_service.auth_service.get_user_by_id', return_value=mock_user):
                from src.main import app
                client = TestClient(app)

                response = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )

                # Should still be valid
                assert response.status_code == 200

    def test_expired_token_error_message(self):
        """Test that expired token returns appropriate error message."""
        expired_token = self.create_expired_token()

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        # Error message should be generic to not leak information
        detail = response.json().get("detail", "")
        assert "invalid" in detail.lower() or "expired" in detail.lower() or "authentication" in detail.lower()


class TestTokenExpiryWithRealTimeWait:
    """Test token expiry with actual time waiting (slower tests)."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        self.original_secret = os.environ.get("BETTER_AUTH_SECRET")
        self.original_database_url = os.environ.get("DATABASE_URL")

        os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-purposes-only"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"

        yield

        if self.original_secret:
            os.environ["BETTER_AUTH_SECRET"] = self.original_secret
        else:
            os.environ.pop("BETTER_AUTH_SECRET", None)

        if self.original_database_url:
            os.environ["DATABASE_URL"] = self.original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

    @pytest.fixture
    def mock_user(self):
        """Create a mock user object."""
        from src.models.user import User
        mock = MagicMock(spec=User)
        mock.id = 1
        mock.email = "test@example.com"
        mock.is_active = True
        return mock

    @pytest.mark.slow
    def test_token_becomes_invalid_after_expiry(self, mock_user):
        """Test that a token becomes invalid after it expires."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        # Create a token that expires in 2 seconds
        payload = {
            "sub": "1",
            "user_id": 1,
            "email": "test@example.com",
            "iat": current_time,
            "exp": current_time + 2
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        mock_db_session = MagicMock()

        from src.main import app
        client = TestClient(app)

        # Token should be valid now
        with patch('src.database.get_session', return_value=mock_db_session):
            with patch('src.services.auth_service.auth_service.get_user_by_id', return_value=mock_user):
                response1 = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert response1.status_code == 200

        # Wait for token to expire
        time.sleep(3)

        # Token should now be invalid
        response2 = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response2.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__])
