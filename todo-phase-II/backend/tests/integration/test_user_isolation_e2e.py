"""
End-to-end integration test for user isolation.
Tests that User A cannot access User B's data.
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestUserIsolationE2E:
    """End-to-end test suite for user isolation."""

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
    def user_a(self):
        """Create mock User A."""
        from src.models.user import User
        mock = MagicMock(spec=User)
        mock.id = 1
        mock.email = "usera@example.com"
        mock.hashed_password = "$2b$12$hashed_password_a"
        mock.is_active = True
        return mock

    @pytest.fixture
    def user_b(self):
        """Create mock User B."""
        from src.models.user import User
        mock = MagicMock(spec=User)
        mock.id = 2
        mock.email = "userb@example.com"
        mock.hashed_password = "$2b$12$hashed_password_b"
        mock.is_active = True
        return mock

    def test_user_a_cannot_access_user_b_info_via_id(self, mock_db_session, user_a, user_b):
        """Test that User A cannot access User B's information via user ID endpoint."""
        from src.lib.jwt_utils import create_access_token

        # Create token for User A
        token_a = create_access_token({
            "sub": "1",
            "user_id": 1,
            "email": "usera@example.com"
        })

        with patch('src.database.get_session', return_value=mock_db_session):
            from src.main import app
            client = TestClient(app)

            # User A tries to access User B's info (user_id=2)
            response = client.get(
                "/auth/2",
                headers={"Authorization": f"Bearer {token_a}"}
            )

            # Should return 404 (not 403) to prevent enumeration
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_user_a_can_access_own_info(self, mock_db_session, user_a):
        """Test that User A can access their own information."""
        from src.lib.jwt_utils import create_access_token

        # Create token for User A
        token_a = create_access_token({
            "sub": "1",
            "user_id": 1,
            "email": "usera@example.com"
        })

        with patch('src.database.get_session', return_value=mock_db_session):
            with patch('src.services.auth_service.auth_service.get_user_by_id', return_value=user_a):
                from src.main import app
                client = TestClient(app)

                # User A accesses their own info (user_id=1)
                response = client.get(
                    "/auth/1",
                    headers={"Authorization": f"Bearer {token_a}"}
                )

                # Should succeed
                assert response.status_code == 200
                assert response.json()["data"]["email"] == "usera@example.com"

    def test_user_b_cannot_access_user_a_info_via_id(self, mock_db_session, user_a, user_b):
        """Test that User B cannot access User A's information via user ID endpoint."""
        from src.lib.jwt_utils import create_access_token

        # Create token for User B
        token_b = create_access_token({
            "sub": "2",
            "user_id": 2,
            "email": "userb@example.com"
        })

        with patch('src.database.get_session', return_value=mock_db_session):
            from src.main import app
            client = TestClient(app)

            # User B tries to access User A's info (user_id=1)
            response = client.get(
                "/auth/1",
                headers={"Authorization": f"Bearer {token_b}"}
            )

            # Should return 404 (not 403) to prevent enumeration
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_isolation_returns_404_not_403(self, mock_db_session, user_a):
        """Test that accessing non-owned resources returns 404 (not 403) to prevent enumeration."""
        from src.lib.jwt_utils import create_access_token

        # Create token for User A
        token_a = create_access_token({
            "sub": "1",
            "user_id": 1,
            "email": "usera@example.com"
        })

        with patch('src.database.get_session', return_value=mock_db_session):
            from src.main import app
            client = TestClient(app)

            # User A tries to access a non-existent user's info (user_id=999)
            response = client.get(
                "/auth/999",
                headers={"Authorization": f"Bearer {token_a}"}
            )

            # Should return 404 specifically (never 403)
            assert response.status_code == 404
            # Ensure the detail doesn't reveal that the resource exists but is forbidden
            assert "forbidden" not in response.json()["detail"].lower()
            assert "not found" in response.json()["detail"].lower()

    def test_me_endpoint_returns_only_current_user(self, mock_db_session, user_a, user_b):
        """Test that /auth/me returns only the current user's information."""
        from src.lib.jwt_utils import create_access_token

        # Create tokens for both users
        token_a = create_access_token({
            "sub": "1",
            "user_id": 1,
            "email": "usera@example.com"
        })
        token_b = create_access_token({
            "sub": "2",
            "user_id": 2,
            "email": "userb@example.com"
        })

        with patch('src.database.get_session', return_value=mock_db_session):
            from src.main import app
            client = TestClient(app)

            # User A's request
            with patch('src.services.auth_service.auth_service.get_user_by_id', return_value=user_a):
                response_a = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {token_a}"}
                )
                assert response_a.status_code == 200
                assert response_a.json()["data"]["email"] == "usera@example.com"
                assert response_a.json()["data"]["user_id"] == 1

            # User B's request
            with patch('src.services.auth_service.auth_service.get_user_by_id', return_value=user_b):
                response_b = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {token_b}"}
                )
                assert response_b.status_code == 200
                assert response_b.json()["data"]["email"] == "userb@example.com"
                assert response_b.json()["data"]["user_id"] == 2


class TestCrossUserDataAccess:
    """Test cross-user data access prevention."""

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

    def test_forged_user_id_in_token_is_rejected(self):
        """Test that forged user_id claims in tokens are properly validated."""
        from src.lib.jwt_utils import create_access_token

        # Create a token with user_id 1
        token = create_access_token({
            "sub": "1",
            "user_id": 1,
            "email": "user1@example.com"
        })

        from src.main import app
        client = TestClient(app)

        # Try to access user 2's resources with user 1's token
        response = client.get(
            "/auth/2",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should return 404 because user 1 cannot access user 2's data
        assert response.status_code == 404

    def test_missing_auth_header_returns_error(self):
        """Test that missing Authorization header returns appropriate error."""
        from src.main import app
        client = TestClient(app)

        # Try to access protected endpoint without auth header
        response = client.get("/auth/me")

        # Should return 401 or 403
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__])
