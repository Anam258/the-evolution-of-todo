# ADR-001: In-Memory to SQLite Storage Evolution Path

**Status**: Accepted
**Date**: 2025-12-30
**Deciders**: Architecture Team
**Context**: Phase I Todo CRUD Feature (001-todo-crud)

## Context and Problem Statement

Phase I requires in-memory storage (no persistence) for simplicity, but Phase II will require SQLite file storage, and Phase III+ will require PostgreSQL cloud storage. How do we design Phase I to enable storage migration without rewriting the CLI/UI layer?

**Key Requirements**:
- Phase I: In-memory dictionary storage (simple, fast, no dependencies)
- Phase II: SQLite file storage (persistent across restarts)
- Phase III+: PostgreSQL cloud storage (scalable, multi-user ready)
- **Constraint**: CLI handlers should remain unchanged across all phases
- **Constraint**: Task entity schema should remain stable (backward compatible)

## Decision Drivers

1. **Constitution Principle IV**: Phase I architecture must support Phase II-V evolution
2. **Constitution Principle VII**: Simplicity/YAGNI - avoid premature abstraction
3. **Hackathon Evaluation**: Judges value architectural foresight and clean design
4. **Development Speed**: Minimize Phase II migration effort while keeping Phase I simple
5. **Type Safety**: Maintain strong typing for IDE support and error prevention

## Considered Options

### Option 1: Direct Dictionary Manipulation (No Abstraction)

**Approach**: CLI handlers directly manipulate `tasks: Dict[int, Task]` global variable

**Pros**:
- Simplest implementation (fewest lines of code)
- No extra classes or indirection
- Fastest Phase I development

**Cons**:
- Phase II requires rewriting all CLI handlers to use SQLite
- Global state makes testing difficult
- Business logic scattered across handlers
- Violates single responsibility principle

**Rejected**: Unacceptable Phase II migration cost, violates constitution requirement for evolution readiness.

### Option 2: Repository Pattern with Interface

**Approach**: Define `ITaskRepository` interface, implement `InMemoryTaskRepository` (Phase I) and `SQLiteTaskRepository` (Phase II)

**Pros**:
- Fully abstracted storage layer
- Swap implementations via dependency injection
- Follows SOLID principles
- Easy to add new storage backends

**Cons**:
- Over-engineered for Phase I (only 1 implementation)
- Requires interface definition (extra complexity)
- Violates YAGNI principle (premature abstraction)
- Adds boilerplate code

**Rejected**: Violates constitution Principle VII (Simplicity/YAGNI). Acceptable pattern for Phase II+ but premature in Phase I.

### Option 3: TaskManager Service with Storage Encapsulation ✅ **SELECTED**

**Approach**: Single `TaskManager` class encapsulates storage (`Dict[int, Task]`) and exposes CRUD methods. Phase II replaces internal dictionary with SQLite without changing method signatures.

**Pros**:
- Balances simplicity (single class) with evolution readiness (encapsulation)
- CLI handlers depend only on `TaskManager` methods, not storage implementation
- Business logic centralized in one place
- Easy to test (inject mock TaskManager)
- Phase II: Replace dict operations with SQLite calls, no UI changes
- Follows single responsibility (TaskManager owns storage, handlers own UI)

**Cons**:
- One layer of indirection vs. direct dict manipulation
- Slightly more code than Option 1 (acceptable trade-off)

**Selected**: Best balance of Phase I simplicity and Phase II-V evolution support.

## Decision

**Use TaskManager service class** to encapsulate in-memory storage with method signatures compatible across all phases.

### Phase I Implementation

```python
class TaskManager:
    """Manages task CRUD operations with in-memory storage."""

    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, title: str, description: str = "") -> Tuple[bool, str, Optional[Task]]:
        """Create task with auto-assigned ID."""
        if not title.strip():
            return (False, "Title cannot be empty.", None)

        task = Task(id=self._next_id, title=title.strip(), description=description)
        self._tasks[self._next_id] = task
        self._next_id += 1
        return (True, f"Task {task.id} created successfully.", task)

    def get_all(self) -> List[Task]:
        """Retrieve all tasks."""
        return list(self._tasks.values())

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieve task by ID."""
        return self._tasks.get(task_id)

    def update(self, task_id: int, title: Optional[str] = None,
               description: Optional[str] = None) -> Tuple[bool, str]:
        """Update task fields."""
        task = self.get_by_id(task_id)
        if not task:
            return (False, f"Task ID {task_id} does not exist.")

        if title is not None:
            if not title.strip():
                return (False, "Title cannot be empty.")
            task.title = title.strip()

        if description is not None:
            task.description = description

        return (True, f"Task {task_id} updated successfully.")

    def delete(self, task_id: int) -> Tuple[bool, str]:
        """Delete task by ID."""
        if task_id not in self._tasks:
            return (False, f"Task ID {task_id} does not exist.")

        del self._tasks[task_id]
        return (True, f"Task {task_id} deleted successfully.")

    def toggle_complete(self, task_id: int) -> Tuple[bool, str]:
        """Toggle task completion status."""
        task = self.get_by_id(task_id)
        if not task:
            return (False, f"Task ID {task_id} does not exist.")

        task.is_complete = not task.is_complete
        status = "complete" if task.is_complete else "incomplete"
        return (True, f"Task {task_id} marked as {status}.")
```

### Phase II Migration Path

**Step 1**: Add SQLite dependency to requirements.txt
```
# requirements.txt (Phase II)
sqlalchemy==2.0.23
```

**Step 2**: Replace TaskManager internals with SQLAlchemy ORM
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TaskManager:
    """Manages task CRUD operations with SQLite storage."""

    def __init__(self, db_path: str = "tasks.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create(self, title: str, description: str = "") -> Tuple[bool, str, Optional[Task]]:
        """Create task with database auto-increment ID."""
        if not title.strip():
            return (False, "Title cannot be empty.", None)

        task = Task(title=title.strip(), description=description)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)  # Get auto-assigned ID
        return (True, f"Task {task.id} created successfully.", task)

    def get_all(self) -> List[Task]:
        """Retrieve all tasks from database."""
        return self.session.query(Task).all()

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieve task by ID from database."""
        return self.session.query(Task).filter(Task.id == task_id).first()

    # update, delete, toggle_complete: Similar pattern (query instead of dict lookup)
```

**Step 3**: Update Task model to ORM class (shown in data-model.md)

**Step 4**: CLI handlers remain **100% unchanged** (still call `task_manager.create()`, etc.)

### Phase III+ Migration Path

**PostgreSQL Migration**:
- Change connection string: `create_engine("postgresql://user:pass@host/db")`
- Add psycopg2 dependency
- TaskManager methods unchanged
- CLI handlers unchanged

**Rationale**: SQLAlchemy abstracts database differences; same ORM code works for SQLite, PostgreSQL, MySQL, etc.

## Consequences

### Positive

✅ **Phase I Simplicity**: Single class, no interfaces, minimal code
✅ **Phase II Migration**: Replace TaskManager internals, zero CLI changes
✅ **Phase III+ Cloud Ready**: Drop-in PostgreSQL support via ORM
✅ **Testability**: Easy to mock TaskManager for CLI handler tests
✅ **Business Logic Centralization**: All validation in one place (not scattered)
✅ **Type Safety**: Method signatures use type hints (IDE autocomplete)
✅ **Hackathon Value**: Demonstrates architectural foresight to judges

### Negative

⚠️ **One Layer of Indirection**: CLI handlers call TaskManager, not dict directly (acceptable trade-off per Complexity Tracking)
⚠️ **Phase I Complexity**: ~100 lines of TaskManager code vs. ~20 lines for global dict (justified by evolution requirement)

### Neutral

- TaskManager is not a "repository" (no interface) but provides similar encapsulation
- Phase I uses plain dataclass, Phase II converts to ORM model (schema unchanged)
- ID generation logic changes (counter → autoincrement) but remains transparent to callers

## Validation

**Constitution Check**:
- ✅ Principle IV (Phase-Based Evolution): Architecture supports I→II→III+ migration
- ✅ Principle VII (Simplicity/YAGNI): Minimal abstraction justified by evolution requirement
- ✅ Complexity Tracking: Trade-off documented in plan.md

**Success Criteria**:
- Phase I: TaskManager enables in-memory CRUD with clear API
- Phase II: Storage swap requires <50 lines of code change, zero CLI changes
- Phase III+: PostgreSQL migration via connection string change only

## Implementation Notes

**Phase I Development Order**:
1. Implement Task dataclass (models/task.py)
2. Implement TaskManager with dict storage (services/task_manager.py)
3. Implement CLI handlers using TaskManager methods (cli/handlers.py)
4. Test isolation: TaskManager unit testable without CLI code

**Phase II Migration Checklist**:
- [ ] Add SQLAlchemy to requirements.txt
- [ ] Convert Task dataclass to ORM model
- [ ] Replace TaskManager `__init__` (add DB connection)
- [ ] Replace dict operations with session queries
- [ ] Add migration script for existing data (if applicable)
- [ ] Verify CLI handlers unchanged (git diff should show zero changes)

**Phase III+ Migration Checklist**:
- [ ] Deploy PostgreSQL instance (cloud provider)
- [ ] Update connection string with environment variable
- [ ] Add psycopg2 or asyncpg dependency
- [ ] Test connection and CRUD operations
- [ ] Verify CLI handlers unchanged

## Related Decisions

- **ADR-002**: No External Dependencies (Phase I) - Explains why no ORM in Phase I
- **ADR-003** (Future): SQLite vs. JSON File Storage - Comparison for Phase II options
- **ADR-004** (Future): ORM Selection (SQLAlchemy vs. Peewee) - Phase II implementation choice

## References

- [Constitution Principle IV](../../.specify/memory/constitution.md#iv-phase-based-evolution-non-negotiable)
- [Constitution Principle VII](../../.specify/memory/constitution.md#vii-simplicity-and-yagni-non-negotiable)
- [Plan: Complexity Tracking](plan.md#complexity-tracking)
- [Data Model: Phase II Evolution Path](data-model.md#phase-ii-evolution-path)
