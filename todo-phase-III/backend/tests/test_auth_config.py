"""
Test suite for auth configuration and startup validation.
Tests that the application properly validates required authentication configuration at startup.
"""

import pytest
import os
from unittest.mock import patch


class TestAuthConfigStartup:
    """Test suite for authentication configuration startup validation."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        # Store original values
        self.original_secret = os.environ.get("BETTER_AUTH_SECRET")
        self.original_database_url = os.environ.get("DATABASE_URL")

        # Set required environment variables for tests
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
        os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-purposes-only"

        yield

        # Restore original values
        if self.original_secret:
            os.environ["BETTER_AUTH_SECRET"] = self.original_secret
        else:
            os.environ.pop("BETTER_AUTH_SECRET", None)

        if self.original_database_url:
            os.environ["DATABASE_URL"] = self.original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

    def test_startup_validation_passes_with_valid_secret(self):
        """Test that startup validation passes when BETTER_AUTH_SECRET is properly configured."""
        from src.config.auth_config import validate_startup_configuration, AuthConfig

        # Should not raise any exception
        try:
            validate_startup_configuration()
            assert True
        except ValueError:
            pytest.fail("validate_startup_configuration should not raise ValueError with valid secret")

    def test_startup_validation_fails_with_missing_secret(self):
        """Test that startup validation fails when BETTER_AUTH_SECRET is missing."""
        # Temporarily remove the secret
        original = os.environ.get("BETTER_AUTH_SECRET")
        os.environ.pop("BETTER_AUTH_SECRET", None)

        try:
            from src.config.auth_config import AuthConfig

            # Creating a new AuthConfig instance should fail
            with pytest.raises(ValueError) as exc_info:
                AuthConfig()

            assert "BETTER_AUTH_SECRET" in str(exc_info.value)
            assert "not set" in str(exc_info.value).lower()
        finally:
            # Restore the secret
            if original:
                os.environ["BETTER_AUTH_SECRET"] = original

    def test_startup_validation_fails_with_short_secret(self):
        """Test that startup validation fails when BETTER_AUTH_SECRET is too short."""
        # Temporarily set a short secret
        original = os.environ.get("BETTER_AUTH_SECRET")
        os.environ["BETTER_AUTH_SECRET"] = "short"

        try:
            from src.config.auth_config import AuthConfig

            # Creating a new AuthConfig instance should fail due to short secret
            with pytest.raises(ValueError) as exc_info:
                AuthConfig()

            assert "32 characters" in str(exc_info.value).lower()
        finally:
            # Restore the original secret
            if original:
                os.environ["BETTER_AUTH_SECRET"] = original
            else:
                os.environ.pop("BETTER_AUTH_SECRET", None)

    def test_startup_validation_fails_with_empty_secret(self):
        """Test that startup validation fails when BETTER_AUTH_SECRET is empty."""
        # Temporarily set an empty secret
        original = os.environ.get("BETTER_AUTH_SECRET")
        os.environ["BETTER_AUTH_SECRET"] = ""

        try:
            from src.config.auth_config import AuthConfig

            # Creating a new AuthConfig instance should fail due to empty secret
            with pytest.raises(ValueError) as exc_info:
                AuthConfig()

            assert "not set" in str(exc_info.value).lower()
        finally:
            # Restore the original secret
            if original:
                os.environ["BETTER_AUTH_SECRET"] = original
            else:
                os.environ.pop("BETTER_AUTH_SECRET", None)

    def test_validate_startup_configuration_checks_algorithm(self):
        """Test that startup validation checks for valid JWT algorithm."""
        # Temporarily set an invalid algorithm
        original_algo = os.environ.get("JWT_ALGORITHM")
        os.environ["JWT_ALGORITHM"] = "INVALID_ALGO"

        try:
            from src.config.auth_config import validate_startup_configuration

            # Validation should fail with invalid algorithm
            with pytest.raises(ValueError) as exc_info:
                validate_startup_configuration()

            assert "algorithm" in str(exc_info.value).lower()
        finally:
            # Restore the original algorithm
            if original_algo:
                os.environ["JWT_ALGORITHM"] = original_algo
            else:
                os.environ.pop("JWT_ALGORITHM", None)

    def test_auth_config_get_secret_key(self):
        """Test that AuthConfig.get_secret_key() returns the configured secret."""
        from src.config.auth_config import auth_config

        secret = auth_config.get_secret_key()

        assert secret is not None
        assert len(secret) >= 32

    def test_auth_config_is_valid_secret_key(self):
        """Test that AuthConfig.is_valid_secret_key() returns True for valid secret."""
        from src.config.auth_config import auth_config

        is_valid = auth_config.is_valid_secret_key()

        assert is_valid is True

    def test_auth_config_expiration_default(self):
        """Test that AuthConfig uses default expiration of 24 hours (1440 minutes)."""
        from src.config.auth_config import auth_config

        # Default should be 1440 minutes (24 hours)
        assert auth_config.access_token_expire_minutes == 1440

    def test_auth_config_algorithm_default(self):
        """Test that AuthConfig uses HS256 algorithm by default."""
        from src.config.auth_config import auth_config

        assert auth_config.algorithm == "HS256"


class TestSettingsIntegration:
    """Test settings integration with auth configuration."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        self.original_secret = os.environ.get("BETTER_AUTH_SECRET")
        self.original_database_url = os.environ.get("DATABASE_URL")

        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
        os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-purposes-only"

        yield

        if self.original_secret:
            os.environ["BETTER_AUTH_SECRET"] = self.original_secret
        else:
            os.environ.pop("BETTER_AUTH_SECRET", None)

        if self.original_database_url:
            os.environ["DATABASE_URL"] = self.original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

    def test_settings_loads_better_auth_secret(self):
        """Test that Settings class loads BETTER_AUTH_SECRET from environment."""
        # Force reload of settings module to pick up env changes
        import importlib
        import src.config.settings as settings_module
        importlib.reload(settings_module)

        from src.config.settings import Settings

        # Create a new settings instance
        settings = Settings()

        assert settings.better_auth_secret == "test-secret-key-for-testing-purposes-only"

    def test_settings_loads_jwt_algorithm(self):
        """Test that Settings class loads JWT_ALGORITHM with default value."""
        import importlib
        import src.config.settings as settings_module
        importlib.reload(settings_module)

        from src.config.settings import Settings

        settings = Settings()

        assert settings.jwt_algorithm == "HS256"


if __name__ == "__main__":
    pytest.main([__file__])
