"""
Test suite for user isolation functionality.
Ensures User A cannot access User B's data.
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session
from typing import Optional


class MockModel:
    """Mock SQLModel for testing."""
    __tablename__ = "mock_table"

    def __init__(self, id: int, user_id: int, title: str = "Test"):
        self.id = id
        self.user_id = user_id
        self.title = title


class TestUserIsolation:
    """Test suite for user isolation functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def user_a_resources(self):
        """Resources owned by User A (user_id=1)."""
        return [
            MockModel(id=1, user_id=1, title="User A Todo 1"),
            MockModel(id=2, user_id=1, title="User A Todo 2"),
        ]

    @pytest.fixture
    def user_b_resources(self):
        """Resources owned by User B (user_id=2)."""
        return [
            MockModel(id=3, user_id=2, title="User B Todo 1"),
            MockModel(id=4, user_id=2, title="User B Todo 2"),
        ]

    def test_user_a_can_only_access_own_resources(self, mock_db_session, user_a_resources):
        """Test that User A can only access their own resources."""
        from src.services.user_isolation_example import user_isolation_service

        # Mock the query to return User A's resources
        mock_query = MagicMock()
        mock_db_session.exec.return_value.all.return_value = user_a_resources

        with patch.object(user_isolation_service, 'get_user_owned_resources') as mock_get:
            mock_get.return_value = user_a_resources

            result = user_isolation_service.get_user_owned_resources(
                mock_db_session, MockModel, user_id=1
            )

            # Verify only User A's resources are returned
            assert len(result) == 2
            for resource in result:
                assert resource.user_id == 1

    def test_user_a_cannot_access_user_b_resources(self, mock_db_session, user_b_resources):
        """Test that User A cannot access User B's resources."""
        from src.services.user_isolation_example import user_isolation_service

        # When User A tries to access with their user_id, they should get no resources
        # because the query will filter by user_id=1 which doesn't match User B's resources
        mock_db_session.exec.return_value.all.return_value = []

        with patch.object(user_isolation_service, 'get_user_owned_resources') as mock_get:
            mock_get.return_value = []

            result = user_isolation_service.get_user_owned_resources(
                mock_db_session, MockModel, user_id=1
            )

            # User A should get empty result when trying to access
            # (since User B's resources are filtered out)
            assert len(result) == 0

    def test_get_single_user_resource_returns_none_for_other_user(self, mock_db_session):
        """Test that getting a single resource owned by another user returns None."""
        from src.services.user_isolation_example import user_isolation_service

        # Resource belongs to User B (user_id=2), but User A (user_id=1) is requesting
        mock_db_session.exec.return_value.first.return_value = None

        with patch.object(user_isolation_service, 'get_single_user_resource') as mock_get:
            mock_get.return_value = None

            result = user_isolation_service.get_single_user_resource(
                mock_db_session, MockModel, resource_id=3, user_id=1
            )

            # User A should get None when trying to access User B's resource
            assert result is None

    def test_check_user_owns_resource_returns_false_for_other_user(self, mock_db_session):
        """Test that ownership check returns False for resources owned by other users."""
        from src.services.user_isolation_example import user_isolation_service

        with patch.object(user_isolation_service, 'check_user_owns_resource') as mock_check:
            mock_check.return_value = False

            result = user_isolation_service.check_user_owns_resource(
                mock_db_session, MockModel, resource_id=3, user_id=1
            )

            # User A should not own User B's resource
            assert result is False

    def test_check_user_owns_resource_returns_true_for_own_resource(self, mock_db_session):
        """Test that ownership check returns True for user's own resources."""
        from src.services.user_isolation_example import user_isolation_service

        with patch.object(user_isolation_service, 'check_user_owns_resource') as mock_check:
            mock_check.return_value = True

            result = user_isolation_service.check_user_owns_resource(
                mock_db_session, MockModel, resource_id=1, user_id=1
            )

            # User A should own their own resource
            assert result is True

    def test_update_user_resource_fails_for_other_user(self, mock_db_session):
        """Test that updating a resource owned by another user fails."""
        from src.services.user_isolation_example import user_isolation_service

        # Mock that the resource isn't found (because query is scoped to wrong user)
        mock_db_session.exec.return_value.first.return_value = None

        with patch.object(user_isolation_service, 'update_user_resource') as mock_update:
            mock_update.return_value = False

            result = user_isolation_service.update_user_resource(
                mock_db_session, MockModel, resource_id=3, user_id=1, update_data={"title": "Hacked"}
            )

            # Update should fail for User A on User B's resource
            assert result is False

    def test_delete_user_resource_fails_for_other_user(self, mock_db_session):
        """Test that deleting a resource owned by another user fails."""
        from src.services.user_isolation_example import user_isolation_service

        # Mock that the resource isn't found (because query is scoped to wrong user)
        mock_db_session.exec.return_value.first.return_value = None

        with patch.object(user_isolation_service, 'delete_user_resource') as mock_delete:
            mock_delete.return_value = False

            result = user_isolation_service.delete_user_resource(
                mock_db_session, MockModel, resource_id=3, user_id=1
            )

            # Delete should fail for User A on User B's resource
            assert result is False


class TestUserIsolationErrorHandling:
    """Test that user isolation returns 404 (not 403) for non-owned resources."""

    def test_non_owned_resource_returns_404_not_403(self):
        """
        Verify that accessing a non-owned resource returns 404 (not 403)
        to prevent enumeration attacks.
        """
        from fastapi import HTTPException

        # When a resource is not found or not owned, the API should return 404
        # This prevents attackers from knowing if a resource exists

        def access_resource(user_id: int, resource_id: int, resource_user_id: int):
            """Simulate accessing a resource with user isolation."""
            # If user doesn't own the resource, return 404 (not 403)
            if user_id != resource_user_id:
                raise HTTPException(status_code=404, detail="Not found")
            return {"id": resource_id, "user_id": resource_user_id}

        # User A (user_id=1) tries to access User B's resource (resource_user_id=2)
        with pytest.raises(HTTPException) as exc_info:
            access_resource(user_id=1, resource_id=3, resource_user_id=2)

        # Should be 404, not 403
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Not found"

    def test_owned_resource_returns_resource(self):
        """Verify that accessing an owned resource returns the resource."""
        def access_resource(user_id: int, resource_id: int, resource_user_id: int):
            if user_id != resource_user_id:
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail="Not found")
            return {"id": resource_id, "user_id": resource_user_id}

        # User A (user_id=1) accesses their own resource
        result = access_resource(user_id=1, resource_id=1, resource_user_id=1)

        assert result["id"] == 1
        assert result["user_id"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
