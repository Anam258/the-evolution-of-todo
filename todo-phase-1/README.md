# The Evolution of Todo - Phase I

A simple, in-memory Python console application for managing todo tasks. This is Phase I of a multi-phase evolution toward a cloud-native AI-powered task management system.

## Overview

Phase I delivers a minimal viable product (MVP) for todo management with basic CRUD operations:

- **Create** tasks with title and optional description
- **View** all tasks with completion status indicators
- **Update** task title and/or description
- **Delete** tasks by ID
- **Mark** tasks as complete or incomplete
- **Sequential ID assignment** starting from 1

**Data Storage**: In-memory dictionary (all data lost on exit)
**Phase II Preview**: Will add SQLite persistence

## Prerequisites

- Python 3.11 or higher
- WSL 2 (Windows Subsystem for Linux) if running on Windows
- No external dependencies required (stdlib only)

## Installation

### Windows Users - WSL 2 Setup

1. **Install WSL 2** (if not already installed):
   ```powershell
   wsl --install
   ```

2. **Open WSL 2 terminal** and navigate to project directory:
   ```bash
   cd /mnt/d/GIAIC/Quarter\ 4/Hackathon/Hackathon\ 2/The-Evolution-of-Todo/todo-phase-1
   ```

3. **Verify Python version**:
   ```bash
   python3 --version  # Should be 3.11+
   ```

### Linux/macOS Users

1. **Navigate to project directory**:
   ```bash
   cd /path/to/todo-phase-1
   ```

2. **Verify Python version**:
   ```bash
   python3 --version  # Should be 3.11+
   ```

## Running the Application

### Quick Start

```bash
python3 src/main.py
```

### Expected Output

```
=== Todo App (Phase I - In-Memory Mode) ===
WARNING: All tasks will be lost when you exit.
Phase II will add persistent storage.

=== Main Menu ===
1. Create Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete
6. Mark Task Incomplete
7. Exit

Enter choice (1-7):
```

## Usage Examples

For detailed usage scenarios and examples, see [specs/001-todo-crud/quickstart.md](specs/001-todo-crud/quickstart.md)

### Basic Workflow

1. **Create a task**:
   ```
   Enter choice (1-7): 1

   --- Create Task ---
   Enter task title: Buy groceries
   Enter description (optional): Milk, eggs, bread
   Task 1 created successfully.
   ```

2. **View all tasks**:
   ```
   Enter choice (1-7): 2

   --- All Tasks ---
   [ ] 1. Buy groceries - Milk, eggs, bread

   Total: 1 task
   ```

3. **Mark task complete**:
   ```
   Enter choice (1-7): 5

   --- Mark Task Complete ---
   Enter task ID: 1
   Task 1 marked as complete.
   ```

4. **Update a task**:
   ```
   Enter choice (1-7): 3

   --- Update Task ---
   Enter task ID: 1
   Current title: Buy groceries
   Current description: Milk, eggs, bread

   Enter new title (press Enter to keep current): Buy groceries and pharmacy
   Enter new description (press Enter to keep current):
   Task 1 updated successfully.
   ```

5. **Delete a task**:
   ```
   Enter choice (1-7): 4

   --- Delete Task ---
   Enter task ID: 1
   Task 1 deleted successfully.
   ```

6. **Exit**:
   ```
   Enter choice (1-7): 7

   Goodbye! All tasks have been cleared from memory.
   (Phase II will add persistent storage)
   ```

## Project Structure

```
todo-phase-1/
├── src/
│   ├── main.py              # Application entry point
│   ├── models/
│   │   └── task.py          # Task dataclass model
│   ├── services/
│   │   └── task_manager.py  # Business logic layer
│   └── cli/
│       ├── display.py       # UI formatting utilities
│       └── handlers.py      # Menu option handlers
├── specs/
│   └── 001-todo-crud/       # Feature specifications
├── docs/
│   └── adrs/                # Architecture Decision Records
├── .gitignore
├── requirements.txt
├── setup.sh
└── README.md
```

## Features

### Phase I Capabilities

✅ **User Story 1 (P1 - MVP)**: Create and view tasks
✅ **User Story 2 (P2)**: Mark tasks complete/incomplete
✅ **User Story 3 (P3)**: Update task details
✅ **User Story 4 (P3)**: Delete tasks

### Input Validation

- Title cannot be empty
- Task ID must be numeric
- Task must exist for update/delete/complete operations
- Menu choice must be 1-7

### Error Handling

- Clear error messages to stderr
- User-friendly validation feedback
- Graceful handling of invalid input

## Limitations (Phase I)

⚠️ **In-Memory Storage**: All tasks are lost when the application exits
⚠️ **No Persistence**: Data is not saved to disk
⚠️ **Single User**: No multi-user support
⚠️ **Console Only**: No web or mobile interface

These limitations will be addressed in future phases.

## Development

### Running Tests

Phase I uses manual validation. See [specs/001-todo-crud/quickstart.md](specs/001-todo-crud/quickstart.md) for test scenarios.

### Contributing

This project follows **Spec-Driven Development (SDD)**:

1. All changes must reference approved specifications in `specs/`
2. No code changes without approved Task IDs
3. See [AGENTS.md](AGENTS.md) for development workflow

## Roadmap

- **Phase II**: SQLite persistence, data export
- **Phase III**: PostgreSQL, advanced search/filtering
- **Phase IV**: REST API, web frontend
- **Phase V**: Cloud deployment, AI-powered features

## License

Educational project for GIAIC Quarter 4 Hackathon.

## Support

For issues or questions:
1. Check [specs/001-todo-crud/quickstart.md](specs/001-todo-crud/quickstart.md) for usage guidance
2. Review specification documents in `specs/001-todo-crud/`
3. Check Architecture Decision Records in `docs/adrs/`

---

**Current Version**: Phase I (In-Memory CRUD)
**Last Updated**: 2025-12-30
