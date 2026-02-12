"""
End-to-end integration test for authentication flow.
Tests the complete flow: register -> login -> access protected resource -> logout.
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestAuthenticationFlow:
    """End-to-end test suite for authentication flow."""

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
    def mock_db_session(self):
        """Create a mock database session."""
        mock_session = MagicMock()
        return mock_session

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

    def test_register_creates_user_and_returns_token(self, mock_db_session, mock_user):
        """Test that registration creates a new user and returns a JWT token."""
        with patch('src.database.get_session', return_value=mock_db_session):
            with patch('src.services.auth_service.auth_service.get_user_by_email', return_value=None):
                with patch('src.services.auth_service.auth_service.create_user', return_value=mock_user):
                    with patch('src.services.auth_service.auth_service.create_access_token_for_user') as mock_token:
                        mock_token.return_value = "test_jwt_token"

                        from src.main import app
                        client = TestClient(app)

                        response = client.post(
                            "/auth/register",
                            json={"email": "test@example.com", "password": "securepassword123"}
                        )

                        # Check response
                        assert response.status_code == 200
                        data = response.json()
                        assert "data" in data
                        assert data["data"]["email"] == "test@example.com"
                        assert "token" in data["data"]

    def test_login_returns_token_for_valid_credentials(self, mock_db_session, mock_user):
        """Test that login returns a JWT token for valid credentials."""
        with patch('src.database.get_session', return_value=mock_db_session):
            with patch('src.services.auth_service.auth_service.authenticate_user', return_value=mock_user):
                with patch('src.services.auth_service.auth_service.create_access_token_for_user') as mock_token:
                    mock_token.return_value = "test_jwt_token"

                    from src.main import app
                    client = TestClient(app)

                    response = client.post(
                        "/auth/login",
                        json={"email": "test@example.com", "password": "securepassword123"}
                    )

                    # Check response
                    assert response.status_code == 200
                    data = response.json()
                    assert "data" in data
                    assert data["data"]["email"] == "test@example.com"
                    assert "token" in data["data"]

    def test_login_returns_401_for_invalid_credentials(self, mock_db_session):
        """Test that login returns 401 for invalid credentials."""
        with patch('src.database.get_session', return_value=mock_db_session):
            with patch('src.services.auth_service.auth_service.authenticate_user', return_value=None):
                from src.main import app
                client = TestClient(app)

                response = client.post(
                    "/auth/login",
                    json={"email": "wrong@example.com", "password": "wrongpassword"}
                )

                # Check response
                assert response.status_code == 401
                assert "Incorrect email or password" in response.json()["detail"]

    def test_protected_endpoint_requires_token(self):
        """Test that protected endpoints require a valid token."""
        from src.main import app
        client = TestClient(app)

        # Try to access protected endpoint without token
        response = client.get("/auth/me")

        # Should return 401 or 403
        assert response.status_code in [401, 403]

    def test_protected_endpoint_accepts_valid_token(self, mock_db_session, mock_user):
        """Test that protected endpoints accept valid tokens."""
        from src.lib.jwt_utils import create_access_token

        # Create a valid token
        token = create_access_token({
            "sub": "1",
            "user_id": 1,
            "email": "test@example.com"
        })

        with patch('src.database.get_session', return_value=mock_db_session):
            with patch('src.services.auth_service.auth_service.get_user_by_id', return_value=mock_user):
                from src.main import app
                client = TestClient(app)

                response = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )

                # Check response
                assert response.status_code == 200
                data = response.json()
                assert "data" in data
                assert data["data"]["email"] == "test@example.com"

    def test_protected_endpoint_rejects_invalid_token(self):
        """Test that protected endpoints reject invalid tokens."""
        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        # Should return 401
        assert response.status_code == 401

    def test_logout_returns_success(self):
        """Test that logout endpoint returns success message."""
        from src.main import app
        client = TestClient(app)

        response = client.post("/auth/logout")

        # Check response
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

    def test_complete_auth_flow(self, mock_db_session, mock_user):
        """Test complete authentication flow: register -> login -> access -> logout."""
        from src.lib.jwt_utils import create_access_token

        with patch('src.database.get_session', return_value=mock_db_session):
            from src.main import app
            client = TestClient(app)

            # Step 1: Register
            with patch('src.services.auth_service.auth_service.get_user_by_email', return_value=None):
                with patch('src.services.auth_service.auth_service.create_user', return_value=mock_user):
                    with patch('src.services.auth_service.auth_service.create_access_token_for_user') as mock_token:
                        mock_token.return_value = create_access_token({
                            "sub": "1",
                            "user_id": 1,
                            "email": "test@example.com"
                        })

                        register_response = client.post(
                            "/auth/register",
                            json={"email": "test@example.com", "password": "securepassword123"}
                        )

                        assert register_response.status_code == 200
                        register_token = register_response.json()["data"]["token"]

            # Step 2: Login
            with patch('src.services.auth_service.auth_service.authenticate_user', return_value=mock_user):
                with patch('src.services.auth_service.auth_service.create_access_token_for_user') as mock_token:
                    mock_token.return_value = create_access_token({
                        "sub": "1",
                        "user_id": 1,
                        "email": "test@example.com"
                    })

                    login_response = client.post(
                        "/auth/login",
                        json={"email": "test@example.com", "password": "securepassword123"}
                    )

                    assert login_response.status_code == 200
                    login_token = login_response.json()["data"]["token"]

            # Step 3: Access protected resource
            with patch('src.services.auth_service.auth_service.get_user_by_id', return_value=mock_user):
                me_response = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {login_token}"}
                )

                assert me_response.status_code == 200
                assert me_response.json()["data"]["email"] == "test@example.com"

            # Step 4: Logout
            logout_response = client.post("/auth/logout")
            assert logout_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])
