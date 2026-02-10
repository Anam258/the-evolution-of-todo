from typing import Optional
from sqlmodel import Session, select
from ..models.user import User, UserCreate
from ..lib.jwt_utils import verify_password, get_password_hash, create_access_token
from datetime import timedelta
import uuid

class AuthService:
    """
    Authentication service handling user authentication and token management.
    """

    def authenticate_user(self, db_session: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            db_session: Database session
            email: User's email address
            password: User's plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        statement = select(User).where(User.email == email)
        user = db_session.exec(statement).first()

        if not user or not verify_password(password, user.hashed_password):
            return None

        return user

    def create_user(self, db_session: Session, user_create: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            db_session: Database session
            user_create: UserCreate object with user details

        Returns:
            Created User object
        """
        # Hash the password
        hashed_password = user_create.hash_password()

        # Create user object with hashed password
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password
        )

        # Add to database
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)

        return db_user

    def get_user_by_email(self, db_session: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by email.

        Args:
            db_session: Database session
            email: User's email address

        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        return db_session.exec(statement).first()

    def get_user_by_id(self, db_session: Session, user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.

        Args:
            db_session: Database session
            user_id: User's ID

        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        return db_session.exec(statement).first()

    def create_access_token_for_user(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create an access token for a user.

        Args:
            user: User object
            expires_delta: Optional timedelta for token expiration

        Returns:
            JWT access token string
        """
        data = {
            "sub": str(user.id),
            "user_id": user.id,
            "email": user.email
        }
        return create_access_token(data=data, expires_delta=expires_delta)

    def is_valid_user_id(self, db_session: Session, user_id: int) -> bool:
        """
        Check if a user ID exists in the database.

        Args:
            db_session: Database session
            user_id: User ID to validate

        Returns:
            True if user exists, False otherwise
        """
        user = self.get_user_by_id(db_session, user_id)
        return user is not None

    def update_user_password(self, db_session: Session, user_id: int, new_password: str) -> bool:
        """
        Update a user's password.

        Args:
            db_session: Database session
            user_id: User's ID
            new_password: New plain text password

        Returns:
            True if update successful, False otherwise
        """
        user = self.get_user_by_id(db_session, user_id)
        if not user:
            return False

        user.hashed_password = get_password_hash(new_password)
        db_session.add(user)
        db_session.commit()
        return True

    def deactivate_user(self, db_session: Session, user_id: int) -> bool:
        """
        Deactivate a user account.

        Args:
            db_session: Database session
            user_id: User's ID

        Returns:
            True if deactivation successful, False otherwise
        """
        user = self.get_user_by_id(db_session, user_id)
        if not user:
            return False

        user.is_active = False
        db_session.add(user)
        db_session.commit()
        return True

    def activate_user(self, db_session: Session, user_id: int) -> bool:
        """
        Activate a user account.

        Args:
            db_session: Database session
            user_id: User's ID

        Returns:
            True if activation successful, False otherwise
        """
        user = self.get_user_by_id(db_session, user_id)
        if not user:
            return False

        user.is_active = True
        db_session.add(user)
        db_session.commit()
        return True


    def scope_query_to_user(self, model_class, user_id: int, additional_filters=None, user_field_name: str = "user_id"):
        """
        Create a SQLModel query scoped to a specific user by adding a filter condition.

        Args:
            model_class: SQLModel class to query
            user_id: User ID to scope the query to
            additional_filters: Additional filter conditions to apply (optional)
            user_field_name: Name of the field that represents the user (default: "user_id")

        Returns:
            Query with user scoping applied
        """
        from sqlmodel import select
        user_column = getattr(model_class, user_field_name)

        query = select(model_class).where(user_column == user_id)

        if additional_filters is not None:
            query = query.where(additional_filters)

        return query

    def create_user_scoped_query(self, model_class, user_id: int, user_field_name: str = "user_id"):
        """
        Create a base query for a model that's already scoped to a specific user.

        Args:
            model_class: SQLModel class to query
            user_id: User ID to scope the query to
            user_field_name: Name of the field that represents the user (default: "user_id")

        Returns:
            Query scoped to the user
        """
        from sqlmodel import select
        user_column = getattr(model_class, user_field_name)
        return select(model_class).where(user_column == user_id)

    def validate_user_owns_resource(self, db_session: Session, resource_model, resource_id: int, user_id: int, user_field_name: str = "user_id") -> bool:
        """
        Validate that a user owns a specific resource.

        Args:
            db_session: Database session
            resource_model: SQLModel model class
            resource_id: ID of the resource to check
            user_id: User ID to validate ownership
            user_field_name: Name of the field that represents the user (default: "user_id")

        Returns:
            True if user owns the resource, False otherwise
        """
        # Create a query to find the resource with the specified ID and user
        statement = select(resource_model).where(
            getattr(resource_model, resource_model.__table__.primary_key.columns.keys()[0]) == resource_id,
            getattr(resource_model, user_field_name) == user_id
        )

        resource = db_session.exec(statement).first()
        return resource is not None


# Global instance for convenience
auth_service = AuthService()