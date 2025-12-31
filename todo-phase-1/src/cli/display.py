"""Display utilities for Phase I Todo CRUD CLI.

This module provides UI formatting functions for menu display, task lists,
and user messages with consistent styling.
"""

from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.task import Task


def print_menu() -> None:
    """Display the main menu with all available options.

    Prints a formatted menu showing all commands the user can execute.
    Menu includes create, view, update, delete, complete, incomplete, and exit options.
    """
    print("\n=== Main Menu ===")
    print("1. Create Task")
    print("2. View All Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete")
    print("6. Mark Task Incomplete")
    print("7. Exit")
    print()


def print_tasks(tasks: List[Task]) -> None:
    """Display a formatted list of tasks.

    Args:
        tasks: List of Task objects to display

    Prints each task with its completion status, ID, title, and description preview.
    Shows "No tasks found" message if list is empty.
    """
    if not tasks:
        print("No tasks found. Create one with option 1!")
    else:
        for task in tasks:
            print(task)  # Uses Task.__str__() for formatting

        print(f"\nTotal: {len(tasks)} task{'s' if len(tasks) != 1 else ''}")
