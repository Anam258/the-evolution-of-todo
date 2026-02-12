"""TaskManager service for Phase I Todo CRUD application.

This module provides the business logic layer for task management operations.
Uses in-memory dictionary storage designed for Phase II SQLite migration.
"""

from typing import Dict, List, Optional, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.task import Task


class TaskManager:
    """Manages task CRUD operations with in-memory storage.

    This class encapsulates all business logic for task management. The storage
    implementation (in-memory dict) can be swapped for SQLite in Phase II without
    changing the public method signatures.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects (in-memory storage)
        _next_id: Counter for sequential ID generation starting from 1
    """

    def __init__(self):
        """Initialize TaskManager with empty storage and ID counter."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, title: str, description: str = "") -> Tuple[bool, str, Optional[Task]]:
        """Create a new task with auto-assigned ID.

        Args:
            title: Task title (required, must be non-empty after stripping)
            description: Optional detailed description of the task

        Returns:
            Tuple of (success, message, task):
                - success: True if task created, False if validation failed
                - message: Success or error message for user feedback
                - task: Created Task object if successful, None if failed
        """
        # Validate title is non-empty
        if not title.strip():
            return (False, "Title cannot be empty.", None)

        # Create task with sequential ID
        task = Task(
            id=self._next_id,
            title=title.strip(),
            description=description,
            is_complete=False
        )

        # Store task and increment ID counter
        self._tasks[self._next_id] = task
        self._next_id += 1

        return (True, f"Task {task.id} created successfully.", task)

    def get_all(self) -> List[Task]:
        """Retrieve all tasks in the system.

        Returns:
            List of all Task objects, ordered by creation (ID ascending).
            Returns empty list if no tasks exist.
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieve a specific task by ID.

        Args:
            task_id: The unique identifier of the task to retrieve

        Returns:
            Task object if found, None if task ID does not exist
        """
        return self._tasks.get(task_id)

    def toggle_complete(self, task_id: int) -> Tuple[bool, str]:
        """Toggle the completion status of a task.

        Args:
            task_id: The unique identifier of the task to toggle

        Returns:
            Tuple of (success, message):
                - success: True if task toggled, False if task not found
                - message: Success or error message for user feedback
        """
        # Validate task exists
        task = self.get_by_id(task_id)
        if task is None:
            return (False, f"Task ID {task_id} does not exist.")

        # Toggle completion status
        task.is_complete = not task.is_complete
        status = "complete" if task.is_complete else "incomplete"

        return (True, f"Task {task_id} marked as {status}.")

    def update(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Tuple[bool, str]:
        """Update an existing task's title and/or description.

        Args:
            task_id: The unique identifier of the task to update
            title: New title (optional, if None title remains unchanged)
            description: New description (optional, if None description remains unchanged)

        Returns:
            Tuple of (success, message):
                - success: True if task updated, False if task not found or validation failed
                - message: Success or error message for user feedback
        """
        # Validate task exists
        task = self.get_by_id(task_id)
        if task is None:
            return (False, f"Task ID {task_id} does not exist.")

        # Validate and update title if provided
        if title is not None:
            if not title.strip():
                return (False, "Title cannot be empty.")
            task.title = title.strip()

        # Update description if provided (can be empty)
        if description is not None:
            task.description = description

        return (True, f"Task {task_id} updated successfully.")

    def delete(self, task_id: int) -> Tuple[bool, str]:
        """Delete a task by ID.

        Args:
            task_id: The unique identifier of the task to delete

        Returns:
            Tuple of (success, message):
                - success: True if task deleted, False if task not found
                - message: Success or error message for user feedback
        """
        # Validate task exists
        if task_id not in self._tasks:
            return (False, f"Task ID {task_id} does not exist.")

        # Remove task from storage
        del self._tasks[task_id]

        return (True, f"Task {task_id} deleted successfully.")
