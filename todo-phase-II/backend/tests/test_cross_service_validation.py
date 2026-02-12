import pytest
import os
from unittest.mock import patch
from src.lib.jwt_utils import create_access_token, verify_token
from src.config.auth_config import verify_shared_secret_configuration, test_cross_service_compatibility


class TestCrossServiceTokenValidation:
    """Test suite for cross-service token validation."""

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

    def test_token_creation_and_verification_with_same_secret(self):
        """Test that tokens created with the secret can be verified by the same service."""
        # Create a test token
        test_data = {"sub": "test_user", "user_id": 123, "email": "test@example.com"}
        token = create_access_token(test_data)

        # Verify the token
        result = verify_token(token)

        # Assert that verification was successful
        assert result is not None
        assert result["sub"] == "test_user"
        assert result["user_id"] == 123
        assert result["email"] == "test@example.com"

    def test_cross_service_compatibility_positive(self):
        """Test that cross-service compatibility check passes with valid configuration."""
        is_compatible, message = test_cross_service_compatibility()

        # The test should pass with a valid configuration
        assert is_compatible is True
        assert "successful" in message.lower()

    def test_shared_secret_validation_passes_with_valid_secret(self):
        """Test that shared secret validation passes with a valid secret."""
        is_valid, error_message = verify_shared_secret_configuration()

        # With a valid secret, validation should pass
        assert is_valid is True
        assert error_message == ""

    def test_shared_secret_validation_fails_with_short_secret(self):
        """Test that shared secret validation fails with a short secret."""
        # Temporarily set a short secret
        original_secret = os.environ.get("BETTER_AUTH_SECRET")
        os.environ["BETTER_AUTH_SECRET"] = "short"

        try:
            is_valid, error_message = verify_shared_secret_configuration()

            # With a short secret, validation should fail
            assert is_valid is False
            assert "too short" in error_message.lower()
        finally:
            # Restore the original secret
            if original_secret:
                os.environ["BETTER_AUTH_SECRET"] = original_secret
            else:
                os.environ.pop("BETTER_AUTH_SECRET", None)

    def test_shared_secret_validation_fails_with_empty_secret(self):
        """Test that shared secret validation fails with an empty secret."""
        # Temporarily set an empty secret
        original_secret = os.environ.get("BETTER_AUTH_SECRET")
        os.environ["BETTER_AUTH_SECRET"] = ""

        try:
            is_valid, error_message = verify_shared_secret_configuration()

            # With an empty secret, validation should fail
            assert is_valid is False
            assert "not set or empty" in error_message.lower()
        finally:
            # Restore the original secret
            if original_secret:
                os.environ["BETTER_AUTH_SECRET"] = original_secret
            else:
                os.environ.pop("BETTER_AUTH_SECRET", None)

    def test_token_cannot_be_verified_with_different_secret(self):
        """Test that tokens created with one secret cannot be verified with a different secret."""
        # Create a token with the current secret
        test_data = {"sub": "test_user", "user_id": 123}
        token = create_access_token(test_data)

        # Temporarily change the secret to simulate a different service with a mismatched secret
        original_secret = os.environ.get("BETTER_AUTH_SECRET")
        os.environ["BETTER_AUTH_SECRET"] = "different-secret-key-for-testing-purposes"

        try:
            # Try to verify the token with the different secret
            result = verify_token(token)

            # Verification should fail with a different secret
            assert result is None
        finally:
            # Restore the original secret
            if original_secret:
                os.environ["BETTER_AUTH_SECRET"] = original_secret
            else:
                os.environ.pop("BETTER_AUTH_SECRET", None)

    def test_cross_service_compatibility_negative(self):
        """Test cross-service compatibility when secrets are mismatched."""
        # Temporarily change the secret to simulate a different service with a mismatched secret
        original_secret = os.environ.get("BETTER_AUTH_SECRET")
        os.environ["BETTER_AUTH_SECRET"] = "different-secret-key-for-testing-purposes"

        try:
            is_compatible, message = test_cross_service_compatibility()

            # With mismatched secrets, compatibility should fail
            assert is_compatible is False
            assert "mismatch" in message.lower() or "failed" in message.lower()
        finally:
            # Restore the original secret
            if original_secret:
                os.environ["BETTER_AUTH_SECRET"] = original_secret
            else:
                os.environ.pop("BETTER_AUTH_SECRET", None)


class TestTokenLifecycle:
    """Test suite for token lifecycle and expiration."""

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

    def test_token_expires_after_set_duration(self):
        """Test that tokens expire after the configured duration."""
        from datetime import timedelta
        from jose import jwt
        import time

        # Create a token that expires in 1 second
        test_data = {"sub": "test_user", "exp": int(time.time()) + 1}
        token = jwt.encode(test_data, os.environ["BETTER_AUTH_SECRET"], algorithm="HS256")

        # Verify the token immediately (should succeed)
        result = verify_token(token)
        assert result is not None

        # Wait for the token to expire
        time.sleep(2)

        # Verify the token after expiration (should fail)
        result = verify_token(token)
        assert result is None

    def test_token_with_past_expiry_cannot_be_verified(self):
        """Test that tokens with past expiry dates cannot be verified."""
        from datetime import datetime, timedelta
        from jose import jwt
        import time

        # Create a token with an expiry in the past
        test_data = {"sub": "test_user", "exp": int(time.time()) - 10}  # 10 seconds ago
        token = jwt.encode(test_data, os.environ["BETTER_AUTH_SECRET"], algorithm="HS256")

        # Verify the token (should fail as it's expired)
        result = verify_token(token)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])