"""Main entry point for Phase I Todo CRUD application.

This module initializes the application, displays startup warnings,
and runs the main menu loop until the user exits.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.task_manager import TaskManager
from cli.display import print_menu
from cli.handlers import handle_create_task, handle_view_tasks, handle_complete_task, handle_incomplete_task, handle_update_task, handle_delete_task


def main():
    """Main application loop.

    Initializes TaskManager, displays startup warning about in-memory storage,
    and runs the interactive menu loop until user chooses to exit.
    """
    # Display startup warning
    print("=== Todo App (Phase I - In-Memory Mode) ===")
    print("WARNING: All tasks will be lost when you exit.")
    print("Phase II will add persistent storage.")
    print()

    # Initialize task manager
    task_manager = TaskManager()

    # Main loop
    while True:
        print_menu()
        choice = input("Enter choice (1-7): ").strip()

        # Validate menu choice
        if choice not in ["1", "2", "3", "4", "5", "6", "7"]:
            print(f"Invalid choice. Please enter 1-7.", file=sys.stderr)
            continue

        # Route to appropriate handler
        if choice == "1":
            handle_create_task(task_manager)
        elif choice == "2":
            handle_view_tasks(task_manager)
        elif choice == "3":
            handle_update_task(task_manager)
        elif choice == "4":
            handle_delete_task(task_manager)
        elif choice == "5":
            handle_complete_task(task_manager)
        elif choice == "6":
            handle_incomplete_task(task_manager)
        elif choice == "7":
            print("\nGoodbye! All tasks have been cleared from memory.")
            print("(Phase II will add persistent storage)")
            break


if __name__ == "__main__":
    main()
