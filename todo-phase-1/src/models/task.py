"""Task model for Phase I Todo CRUD application.

This module defines the Task entity with attributes for id, title, description,
and completion status. Designed for Phase II evolution to ORM model.
"""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a todo task with unique ID, title, description, and completion status.

    Attributes:
        id: Unique sequential identifier, auto-assigned by TaskManager
        title: Short description of the task (required, non-empty)
        description: Optional detailed information about the task
        is_complete: Completion status (defaults to False)
    """

    id: int
    title: str
    description: str = ""
    is_complete: bool = False

    def __str__(self) -> str:
        """Human-readable string representation for console display.

        Returns:
            Formatted string with completion status indicator, ID, title, and description preview.
            Format: "[X] 1. Task title - Description preview..."
                or "[ ] 1. Task title - Description preview..."
        """
        status = "[X]" if self.is_complete else "[ ]"
        desc_preview = f" - {self.description[:50]}..." if len(self.description) > 50 else (f" - {self.description}" if self.description else "")
        return f"{status} {self.id}. {self.title}{desc_preview}"
