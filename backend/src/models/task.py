"""
Task model for the TaskPulse AI application.

Implements the Task entity with user isolation using the UserIsolationService pattern.
Each task is owned by a user and can only be accessed by that user.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .user import User


class TaskBase(SQLModel):
    """Base model containing common fields for Task"""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    """Task model with all fields and relationships"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")

    # Relationship to user (optional)
    user: Optional["User"] = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    """Model for creating new tasks"""
    pass


class TaskRead(TaskBase):
    """Model for reading task data"""
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int


class TaskUpdate(SQLModel):
    """Model for updating existing tasks"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: Optional[bool] = None


class TaskPatch(SQLModel):
    """Model for patching task status"""
    is_completed: bool