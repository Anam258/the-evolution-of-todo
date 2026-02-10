from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """
    User model representing an authenticated user in the system.

    Fields:
    - id: Integer (Primary Key, Auto-increment) - Unique identifier for the user
    - email: String (Unique, Indexed) - User's email address for login
    - hashed_password: String - BCrypt hashed password
    - created_at: DateTime - Timestamp of account creation
    - updated_at: DateTime - Timestamp of last update
    - is_active: Boolean (Default: True) - Whether the account is active
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks (optional)
    tasks: Optional[List["Task"]] = Relationship(back_populates="user")


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserCreate(UserBase):
    password: str  # Plain text password to be hashed

    def hash_password(self) -> str:
        """Hash the plain text password"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(self.password)


class UserUpdate(SQLModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None