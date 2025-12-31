# Data Model: Phase I Todo CRUD

**Feature**: 001-todo-crud
**Created**: 2025-12-30
**Status**: Design Complete

## Overview

Phase I data model consists of a single **Task** entity with four attributes, stored in an in-memory dictionary for O(1) lookup performance. The model is designed for Phase II evolution to SQLite/PostgreSQL without schema changes.

## Entity: Task

### Attributes

| Attribute | Type | Required | Default | Mutable | Description |
|-----------|------|----------|---------|---------|-------------|
| `id` | int | Yes | Auto-assigned | **No** | Unique sequential identifier starting from 1 |
| `title` | str | Yes | None | Yes | Short task description, non-empty string |
| `description` | str | No | Empty string | Yes | Optional detailed information about task |
| `is_complete` | bool | Yes | False | Yes | Completion status, togglable by user |

### Validation Rules

**Field-Level Validation**:
- `id`: Must be positive integer (> 0), auto-assigned by system, never modified after creation
- `title`: Must be non-empty string after stripping whitespace (len(title.strip()) > 0)
- `description`: Any string including empty; treated as optional field
- `is_complete`: Boolean only (True or False)

**Business Rules**:
- **BR-001**: Task IDs are never reused within a session (even after deletion)
- **BR-002**: Task IDs increment sequentially (id_n = id_(n-1) + 1)
- **BR-003**: Title cannot be updated to empty string
- **BR-004**: Description can be updated to empty string (clears description)
- **BR-005**: Deleting a task does not affect IDs of other tasks

### Python Implementation (Phase I)

```python
from dataclasses import dataclass

@dataclass
class Task:
    """Represents a todo task with unique ID, title, description, and completion status."""
    id: int
    title: str
    description: str = ""
    is_complete: bool = False

    def __str__(self) -> str:
        """Human-readable string representation for display."""
        status = "[X]" if self.is_complete else "[ ]"
        desc_preview = f" - {self.description[:50]}..." if self.description else ""
        return f"{status} {self.id}. {self.title}{desc_preview}"
```

**Design Notes**:
- Uses `@dataclass` for automatic `__init__`, `__repr__`, `__eq__` generation
- Type hints enable IDE autocomplete and future type checking
- `__str__` method provides console-friendly display format
- Default values enable flexible object creation

### Phase II Evolution Path

**SQLite Migration** (Phase II):
```python
# Future: SQLAlchemy ORM model (example, not implemented in Phase I)
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False, default="")
    is_complete = Column(Boolean, nullable=False, default=False)
```

**Migration Strategy**:
- Dataclass fields map 1:1 to SQLAlchemy columns (no schema changes)
- ID auto-assignment handled by database autoincrement
- Validation logic remains in TaskManager service layer
- No changes to CLI handlers (depend only on Task interface)

## Storage Structure

### Phase I: In-Memory Dictionary

**Structure**: `Dict[int, Task]`
- **Key**: Task ID (int)
- **Value**: Task object

**Example**:
```python
{
    1: Task(id=1, title="Buy groceries", description="Milk, eggs, bread", is_complete=False),
    2: Task(id=2, title="Write report", description="", is_complete=True),
    5: Task(id=5, title="Call dentist", description="Schedule checkup", is_complete=False)
}
```

**Operations Performance**:
- **Create**: O(1) - Increment counter, insert into dict
- **Read (by ID)**: O(1) - Direct dict lookup
- **Read (all)**: O(n) - Iterate dict.values(), where n = number of tasks
- **Update**: O(1) - Lookup by ID, modify object
- **Delete**: O(1) - Remove from dict by ID
- **Complete/Incomplete**: O(1) - Lookup by ID, toggle boolean

**Storage Manager**:
```python
class TaskManager:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, title: str, description: str = "") -> Tuple[bool, str, Optional[Task]]:
        """Create new task with auto-assigned ID."""
        # Validation: title non-empty
        if not title.strip():
            return (False, "Title cannot be empty.", None)

        # Create task with sequential ID
        task = Task(id=self._next_id, title=title.strip(), description=description)
        self._tasks[self._next_id] = task
        self._next_id += 1

        return (True, f"Task {task.id} created successfully.", task)

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieve task by ID, return None if not found."""
        return self._tasks.get(task_id)

    # Additional methods: get_all, update, delete, toggle_complete
```

### Phase II: SQLite File Storage

**Structure**: SQLite database with `tasks` table

**Migration Steps**:
1. Replace `Dict[int, Task]` with SQLAlchemy session
2. Replace `_next_id` counter with database autoincrement
3. Replace dict operations with ORM queries (create → session.add, get_by_id → session.query)
4. Add database file path configuration
5. CLI handlers remain unchanged (still call TaskManager methods)

**Benefits of Phase I Design**:
- TaskManager abstraction hides storage implementation
- Task dataclass structure matches ORM model
- Validation logic independent of storage mechanism
- No UI changes required for Phase II migration

## Validation Strategy

### Input Validation (CLI Layer)

**CLI handlers validate** before calling TaskManager:
- Menu choice is numeric 1-7
- Task ID input is numeric and positive
- Title input is non-empty after prompting user

**Example** (create task handler):
```python
def handle_create_task(task_manager: TaskManager):
    title = input("Enter task title: ").strip()
    if not title:
        print("Error: Title cannot be empty.", file=sys.stderr)
        return

    description = input("Enter description (optional): ").strip()

    success, message, task = task_manager.create(title, description)
    print(message)
```

### Business Validation (Service Layer)

**TaskManager validates** business rules:
- Title non-empty (double-check even if CLI validates)
- Task ID exists before update/delete/complete operations
- ID is positive integer

**Example** (update task):
```python
def update(self, task_id: int, title: Optional[str] = None,
           description: Optional[str] = None) -> Tuple[bool, str]:
    # Validate task exists
    task = self.get_by_id(task_id)
    if task is None:
        return (False, f"Task ID {task_id} does not exist.")

    # Validate title if provided
    if title is not None:
        if not title.strip():
            return (False, "Title cannot be empty.")
        task.title = title.strip()

    # Update description (can be empty)
    if description is not None:
        task.description = description

    return (True, f"Task {task_id} updated successfully.")
```

## Edge Cases

### Handled in Phase I

1. **Empty title during creation**: Rejected with error message, prompt user to retry
2. **Invalid task ID format** (non-numeric): CLI validates input, shows error before calling TaskManager
3. **Task ID not found**: TaskManager returns (False, "Task ID X does not exist.")
4. **Deleted task ID reuse**: IDs never reused (BR-001), attempts to access deleted ID return "not found" error
5. **Very long title/description** (>1000 chars): Accepted in storage, may truncate in display (future enhancement)
6. **100+ tasks in memory**: Dictionary maintains O(1) performance, display may be unwieldy (acceptable per spec assumption #9)

### Deferred to Future Phases

1. **Data persistence across restarts**: Phase II (SQLite file storage)
2. **Concurrent access / race conditions**: Phase IV (multi-user, locking)
3. **Task relationships / dependencies**: Out of scope per spec
4. **Search / filter / sort**: Out of scope per spec

## Data Lifecycle

### Session Lifecycle

```
Application Start
    ↓
Initialize TaskManager (empty dict, next_id=1)
    ↓
User creates tasks (IDs 1, 2, 3, ...)
    ↓
User performs CRUD operations (dict modified)
    ↓
User exits (choice 7)
    ↓
Application terminates
    ↓
ALL DATA LOST (in-memory only)
```

**User Warning** (displayed at startup):
```
=== Todo App (Phase I - In-Memory Mode) ===
WARNING: All tasks will be lost when you exit.
Phase II will add persistent storage.
```

### Task State Transitions

```
[Create Task]
    ↓
is_complete = False
    ↓
[Mark Complete] ←→ [Mark Incomplete]
    ↓                   ↓
is_complete = True   is_complete = False
    ↓
[Delete Task]
    ↓
(Task removed from memory)
```

**State Invariants**:
- Task always has exactly one completion state (True or False)
- ID never changes after assignment
- Title and description can change independently
- Deletion is irreversible (within session)

## Future Enhancements (Phase II+)

### Phase II: SQLite Storage
- Add `created_at` timestamp (datetime)
- Add `updated_at` timestamp (auto-updated on modifications)
- Consider `deleted_at` for soft deletes (instead of hard delete)

### Phase III: AI Integration
- Add `tags` field (List[str] or separate table)
- Add `priority` field (enum: low/medium/high)
- Add `ai_suggested` flag (bool)

### Phase IV: Multi-User
- Add `user_id` foreign key
- Add `shared_with` many-to-many relationship
- Add `last_modified_by` tracking

### Phase V: Advanced Features
- Add `due_date` field (datetime, nullable)
- Add `recurrence_pattern` (JSON or separate table)
- Add `analytics_metadata` (JSON for ML features)

**Note**: All Phase II+ enhancements are backward-compatible additions (new columns with defaults). Phase I schema remains valid.
