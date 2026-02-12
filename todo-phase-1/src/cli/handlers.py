"""CLI handlers for Phase I Todo CRUD application.

This module provides handler functions for each menu option, including user input
prompts, validation, and interaction with the TaskManager service.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.task_manager import TaskManager


def handle_create_task(task_manager: TaskManager) -> None:
    """Handle the 'Create Task' menu option.

    Prompts user for task title and optional description, validates input,
    and creates the task via TaskManager. Displays success or error message.

    Args:
        task_manager: TaskManager instance for task operations
    """
    print("\n--- Create Task ---")

    # Prompt for title with validation
    title = input("Enter task title: ").strip()
    if not title:
        print("Error: Title cannot be empty.", file=sys.stderr)
        return

    # Prompt for optional description
    description = input("Enter description (optional): ").strip()

    # Create task via TaskManager
    success, message, task = task_manager.create(title, description)

    # Display result
    if success:
        print(message)
    else:
        print(f"Error: {message}", file=sys.stderr)


def handle_view_tasks(task_manager: TaskManager) -> None:
    """Handle the 'View All Tasks' menu option.

    Retrieves all tasks from TaskManager and displays them in a formatted list.
    Shows appropriate message if no tasks exist.

    Args:
        task_manager: TaskManager instance for task operations
    """
    print("\n--- All Tasks ---")

    tasks = task_manager.get_all()

    if not tasks:
        print("No tasks found. Create one with option 1!")
    else:
        for task in tasks:
            print(task)  # Uses Task.__str__() for formatting

        print(f"\nTotal: {len(tasks)} task{'s' if len(tasks) != 1 else ''}")


def handle_complete_task(task_manager: TaskManager) -> None:
    """Handle the 'Mark Task Complete' menu option.

    Prompts user for task ID, validates input, and marks the task as complete.

    Args:
        task_manager: TaskManager instance for task operations
    """
    print("\n--- Mark Task Complete ---")

    # Prompt for task ID with validation
    task_id_input = input("Enter task ID: ").strip()

    try:
        task_id = int(task_id_input)
    except ValueError:
        print("Error: Invalid task ID format. Please enter a number.", file=sys.stderr)
        return

    # Toggle task to complete
    success, message = task_manager.toggle_complete(task_id)

    # Display result
    if success:
        print(message)
    else:
        print(f"Error: {message}", file=sys.stderr)


def handle_incomplete_task(task_manager: TaskManager) -> None:
    """Handle the 'Mark Task Incomplete' menu option.

    Prompts user for task ID, validates input, and marks the task as incomplete.
    Uses the same toggle_complete method (toggles back to incomplete if already complete).

    Args:
        task_manager: TaskManager instance for task operations
    """
    print("\n--- Mark Task Incomplete ---")

    # Prompt for task ID with validation
    task_id_input = input("Enter task ID: ").strip()

    try:
        task_id = int(task_id_input)
    except ValueError:
        print("Error: Invalid task ID format. Please enter a number.", file=sys.stderr)
        return

    # Toggle task to incomplete
    success, message = task_manager.toggle_complete(task_id)

    # Display result
    if success:
        print(message)
    else:
        print(f"Error: {message}", file=sys.stderr)


def handle_update_task(task_manager: TaskManager) -> None:
    """Handle the 'Update Task' menu option.

    Prompts user for task ID and new values for title/description.
    Allows pressing Enter to keep current values unchanged.

    Args:
        task_manager: TaskManager instance for task operations
    """
    print("\n--- Update Task ---")

    # Prompt for task ID with validation
    task_id_input = input("Enter task ID: ").strip()

    try:
        task_id = int(task_id_input)
    except ValueError:
        print("Error: Invalid task ID format. Please enter a number.", file=sys.stderr)
        return

    # Get current task to show current values
    task = task_manager.get_by_id(task_id)
    if task is None:
        print(f"Error: Task ID {task_id} does not exist.", file=sys.stderr)
        return

    print(f"Current title: {task.title}")
    print(f"Current description: {task.description}")
    print()

    # Prompt for new values (press Enter to keep current)
    new_title = input("Enter new title (press Enter to keep current): ").strip()
    new_description = input("Enter new description (press Enter to keep current): ").strip()

    # Determine what to update (None means keep current)
    title_to_update = new_title if new_title else None
    description_to_update = new_description if new_description else None

    # Only update if at least one field changed
    if title_to_update is None and description_to_update is None:
        print("No changes made.")
        return

    # Update task via TaskManager
    success, message = task_manager.update(task_id, title_to_update, description_to_update)

    # Display result
    if success:
        print(message)
    else:
        print(f"Error: {message}", file=sys.stderr)


def handle_delete_task(task_manager: TaskManager) -> None:
    """Handle the 'Delete Task' menu option.

    Prompts user for task ID, validates input, and deletes the task.

    Args:
        task_manager: TaskManager instance for task operations
    """
    print("\n--- Delete Task ---")

    # Prompt for task ID with validation
    task_id_input = input("Enter task ID: ").strip()

    try:
        task_id = int(task_id_input)
    except ValueError:
        print("Error: Invalid task ID format. Please enter a number.", file=sys.stderr)
        return

    # Delete task via TaskManager
    success, message = task_manager.delete(task_id)

    # Display result
    if success:
        print(message)
    else:
        print(f"Error: {message}", file=sys.stderr)
