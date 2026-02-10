"""
User Isolation Service for enforcing data isolation between users.
Ensures that users can only access their own resources.
"""

from sqlmodel import Session, select
from typing import List, Optional, Any, Type
from .auth_service import auth_service


class UserIsolationService:
    """
    Service for enforcing user isolation through database query filtering.
    All database queries for user-owned resources MUST use these methods
    to prevent unauthorized access to other users' data.

    Security: Returns 404 (not 403) for non-owned resources to prevent
    enumeration attacks per spec FR-011.
    """

    def get_user_owned_resources(
        self,
        db_session: Session,
        model_class: Type[Any],
        user_id: int,
        user_field_name: str = "user_id"
    ) -> List[Any]:
        """
        Get all resources owned by a specific user.

        Args:
            db_session: Database session
            model_class: SQLModel class to query
            user_id: User ID whose resources to retrieve
            user_field_name: Name of the field that represents the user (default: "user_id")

        Returns:
            List of resources owned by the user
        """
        query = auth_service.create_user_scoped_query(model_class, user_id, user_field_name)
        return db_session.exec(query).all()

    def get_single_user_resource(
        self,
        db_session: Session,
        model_class: Type[Any],
        resource_id: int,
        user_id: int,
        user_field_name: str = "user_id"
    ) -> Optional[Any]:
        """
        Get a specific resource owned by a user.

        Args:
            db_session: Database session
            model_class: SQLModel class to query
            resource_id: ID of the specific resource to retrieve
            user_id: User ID that should own the resource
            user_field_name: Name of the field that represents the user (default: "user_id")

        Returns:
            Resource if it exists and is owned by the user, None otherwise.
            Return None (which should map to 404) if resource is not owned by user.
        """
        primary_key_field = model_class.__table__.primary_key.columns.keys()[0]
        query = select(model_class).where(
            getattr(model_class, user_field_name) == user_id,
            getattr(model_class, primary_key_field) == resource_id
        )
        return db_session.exec(query).first()

    def check_user_owns_resource(
        self,
        db_session: Session,
        model_class: Type[Any],
        resource_id: int,
        user_id: int,
        user_field_name: str = "user_id"
    ) -> bool:
        """
        Check if a user owns a specific resource.
        Used to determine if a 404 response should be returned.

        Args:
            db_session: Database session
            model_class: SQLModel class to check
            resource_id: ID of the resource to check
            user_id: User ID to validate ownership
            user_field_name: Name of the field that represents the user (default: "user_id")

        Returns:
            True if user owns the resource, False otherwise
        """
        return auth_service.validate_user_owns_resource(
            db_session, model_class, resource_id, user_id, user_field_name
        )

    def update_user_resource(
        self,
        db_session: Session,
        model_class: Type[Any],
        resource_id: int,
        user_id: int,
        update_data: dict,
        user_field_name: str = "user_id"
    ) -> bool:
        """
        Update a resource owned by a user.
        Only updates if the user owns the resource.

        Args:
            db_session: Database session
            model_class: SQLModel class to update
            resource_id: ID of the resource to update
            user_id: User ID that should own the resource
            update_data: Dictionary of field-value pairs to update
            user_field_name: Name of the field that represents the user (default: "user_id")

        Returns:
            True if update was successful, False otherwise
        """
        # First, find the resource that belongs to the user
        resource = self.get_single_user_resource(
            db_session, model_class, resource_id, user_id, user_field_name
        )
        if not resource:
            return False  # Resource doesn't exist or doesn't belong to user

        # Update the resource with new data
        for field, value in update_data.items():
            if hasattr(resource, field):
                setattr(resource, field, value)

        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        return True

    def delete_user_resource(
        self,
        db_session: Session,
        model_class: Type[Any],
        resource_id: int,
        user_id: int,
        user_field_name: str = "user_id"
    ) -> bool:
        """
        Delete a resource owned by a user.
        Only deletes if the user owns the resource.

        Args:
            db_session: Database session
            model_class: SQLModel class to delete from
            resource_id: ID of the resource to delete
            user_id: User ID that should own the resource
            user_field_name: Name of the field that represents the user (default: "user_id")

        Returns:
            True if deletion was successful, False otherwise
        """
        # Find the resource that belongs to the user
        resource = self.get_single_user_resource(
            db_session, model_class, resource_id, user_id, user_field_name
        )
        if not resource:
            return False  # Resource doesn't exist or doesn't belong to user

        db_session.delete(resource)
        db_session.commit()
        return True


# Global instance for convenience
user_isolation_service = UserIsolationService()
