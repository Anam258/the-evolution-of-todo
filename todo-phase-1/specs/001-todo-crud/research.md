# Research: Phase I Todo CRUD

**Feature**: 001-todo-crud
**Date**: 2025-12-30
**Status**: Not Applicable (Greenfield Project)

## Overview

This is a **greenfield project** (new codebase from scratch), so traditional codebase research is not applicable. This document addresses architectural research questions relevant to Phase I implementation and Phase II-V evolution.

## Research Questions & Findings

### Q1: Storage Approach for Phase I→II→III+ Migration

**Question**: What storage structure in Phase I enables smooth migration to SQLite (Phase II) and PostgreSQL (Phase III+)?

**Research Method**: Review constitution requirements, analyze ORM compatibility, compare data structures.

**Findings**:
- **Phase I Requirement**: In-memory only (no persistence), simple implementation
- **Phase II Requirement**: SQLite file storage (persistent across restarts)
- **Phase III+ Requirement**: PostgreSQL cloud storage (scalable, multi-user)

**Decision**: Use **dictionary-based storage** (`Dict[int, Task]`) with `TaskManager` abstraction
- **Rationale**:
  - Dictionary provides O(1) lookups (required for 50-100 task performance)
  - TaskManager abstraction isolates storage logic from UI
  - Task dataclass structure mirrors ORM model (easy conversion)
  - Method signatures remain stable across all phases

**Evidence**: See [ADR-001](../../docs/adrs/001-in-memory-to-sqlite-evolution.md) for detailed analysis

**Alternative Considered**: List-based storage (`List[Task]`)
- **Rejected**: O(n) lookup performance unacceptable at scale; no direct ID-based access; complicates deletion (index shifting vs. ID stability)

### Q2: ID Generation Strategy

**Question**: How should task IDs be generated to support database auto-increment in Phase II?

**Research Method**: Compare ID generation patterns (UUID, sequential int, timestamp-based).

**Findings**:
- **Spec Requirement** (FR-002): "Unique sequential integer ID starting from 1"
- **Database Compatibility**: SQLite and PostgreSQL support auto-increment integer primary keys
- **User Experience**: Sequential IDs easier to reference than UUIDs (e.g., "complete task 5" vs. "complete task a3f2-b4c1...")

**Decision**: Use **sequential integer counter** starting from 1, never reused
- **Phase I**: `TaskManager._next_id` counter, incremented after each creation
- **Phase II**: Database `AUTOINCREMENT` primary key
- **Phase III+**: PostgreSQL `SERIAL` or `IDENTITY` column

**Implementation**:
```python
class TaskManager:
    def __init__(self):
        self._next_id: int = 1

    def create(self, title, description):
        task_id = self._next_id
        # ... create task ...
        self._next_id += 1
```

**Alternative Considered**: UUID4 (universally unique identifier)
- **Rejected**: Violates spec requirement (FR-002 specifies integer); poor UX for manual ID entry; unnecessary for single-user Phase I

### Q3: Error Handling Patterns

**Question**: What error handling approach supports both console output (Phase I) and HTTP status codes (Phase II API)?

**Research Method**: Compare exception-based vs. return-value-based error handling.

**Findings**:
- **Spec Requirement** (FR-007, NFR-004): "Clear error messages for invalid operations"
- **Phase II Requirement**: REST API will need HTTP status codes (200, 404, 400, etc.)

**Decision**: Use **tuple return values** `(success: bool, message: str)` from service methods
- **Rationale**:
  - Explicit error handling (no hidden exceptions)
  - Maps cleanly to HTTP responses: `success=True` → 200 OK, `success=False` → 400/404
  - Forces CLI handlers to handle errors (no silent failures)
  - Pythonic pattern (similar to Go's error returns)

**Implementation**:
```python
def create(self, title, desc) -> Tuple[bool, str, Optional[Task]]:
    if not title.strip():
        return (False, "Title cannot be empty.", None)
    # ... create task ...
    return (True, f"Task {task.id} created successfully.", task)

# CLI handler
success, message, task = task_manager.create(title, desc)
if success:
    print(message)
else:
    print(f"Error: {message}", file=sys.stderr)
```

**Alternative Considered**: Exception-based error handling
- **Rejected**: Exceptions for control flow considered anti-pattern in Python; harder to map to HTTP codes; forces try-catch boilerplate in every handler

### Q4: Input Validation Layer

**Question**: Where should input validation occur (CLI vs. service layer)?

**Research Method**: Analyze separation of concerns, review validation best practices.

**Findings**:
- **Two Validation Layers Needed**:
  1. **CLI Layer**: Format validation (numeric input, non-empty prompts)
  2. **Service Layer**: Business rule validation (title non-empty, task exists)

**Decision**: **Dual-layer validation**
- **CLI Handlers**: Validate input format before calling service
  - Menu choice is 1-7 numeric
  - Task ID is positive integer
  - Prompt user for required fields (don't send empty strings to service)
- **TaskManager**: Validate business rules (double-check + enforce invariants)
  - Title non-empty (defense against CLI bugs)
  - Task ID exists before update/delete/complete
  - No duplicate IDs (internal consistency)

**Rationale**:
- **Defense in Depth**: CLI mistakes don't corrupt data
- **Phase II Readiness**: API layer can reuse TaskManager validation (no CLI dependency)
- **User Experience**: CLI validates early (fast feedback), service validates thoroughly (data integrity)

**Implementation**:
```python
# CLI Layer
def handle_create_task(task_manager):
    title = input("Title: ").strip()
    if not title:  # Format validation
        print("Error: Title required.", file=sys.stderr)
        return
    # Call service
    success, msg, task = task_manager.create(title, desc)

# Service Layer
def create(self, title, desc):
    if not title.strip():  # Business rule validation
        return (False, "Title cannot be empty.", None)
    # ... create task ...
```

## Technology Stack Research

### Python Version Selection

**Requirement**: Python 3.11+ per constitution

**Research Findings**:
- **Python 3.11 Features Used**:
  - Type hints with `Tuple`, `Optional`, `Dict`, `List` (stdlib typing)
  - Dataclasses (stdlib dataclasses module)
  - f-strings for formatting
  - Type checking support (mypy compatible)
- **WSL 2 Availability**: Ubuntu 22.04 LTS ships with Python 3.10, 3.11 available via apt

**Decision**: Target Python 3.11 as minimum version
- **Rationale**: Latest stable, good WSL support, modern type hints

### External Dependencies

**Question**: Should Phase I use any external libraries (CLI framework, validation, etc.)?

**Research Method**: Compare stdlib vs. external libraries for common needs.

**Findings**:
| Need | Stdlib Option | External Option | Decision |
|------|---------------|-----------------|----------|
| CLI menu | `input()` loop | click, typer | **Stdlib** (7 options = simple loop) |
| Data validation | Manual checks | pydantic | **Stdlib** (4 fields = overkill for pydantic) |
| Data storage | `Dict[int, Task]` | SQLAlchemy | **Stdlib** (in-memory = no DB needed) |
| Testing | Manual (quickstart) | pytest | **Manual** (tests not requested) |

**Decision**: **Zero external dependencies** in Phase I
- **Rationale**: Constitution Principle VII (Simplicity/YAGNI) - no dependency justified for current scope
- **Deferred to Phase II**: SQLAlchemy (when SQLite needed), pytest (when tests requested)

**See**: [ADR-002](../../docs/adrs/002-no-external-dependencies-phase-i.md) (placeholder for future creation)

## Codebase Structure Research

**Question**: What Python project structure supports Phase II-V evolution?

**Research Findings**:
- **Patterns Analyzed**:
  - Flat structure (all modules in root)
  - src layout (industry standard for installable packages)
  - Django-style (app-based organization)

**Decision**: Use **src layout** with domain-driven organization
```
src/
├── models/       # Domain entities (Task)
├── services/     # Business logic (TaskManager)
├── cli/          # User interface (handlers, display)
└── main.py       # Application entry point
```

**Rationale**:
- **Industry Standard**: Matches Python packaging best practices
- **Clear Separation**: models ← services ← cli dependency flow
- **Phase II Ready**: Add `api/` folder for REST endpoints, `db/` for migrations
- **Testable**: Each layer independently testable

## Performance Benchmarks (Research)

**Question**: Can dictionary storage meet NFR-002 (<1 second for 100 tasks)?

**Method**: Analyze algorithmic complexity and typical hardware performance.

**Findings**:
| Operation | Complexity | 100 Tasks | 1000 Tasks |
|-----------|------------|-----------|------------|
| Create | O(1) | <1ms | <1ms |
| Get by ID | O(1) | <1ms | <1ms |
| Get all | O(n) | ~1ms | ~10ms |
| Update | O(1) | <1ms | <1ms |
| Delete | O(1) | <1ms | <1ms |
| Complete | O(1) | <1ms | <1ms |

**Conclusion**: Dictionary storage easily meets performance requirements
- **100 tasks**: All operations <1ms (well under 1 second requirement)
- **1000 tasks**: Still acceptable (get_all ~10ms, others <1ms)

**No optimization needed** for Phase I scope (50-100 tasks per spec assumption #9)

## Security Research

**Question**: What input sanitization is needed for Phase I console app?

**Findings**:
- **No SQL Injection Risk**: In-memory storage (no SQL queries)
- **No XSS Risk**: Console output only (no HTML rendering)
- **No Command Injection Risk**: No shell command execution
- **Title Validation**: Check non-empty, but accept any string content

**Decision**: Minimal validation sufficient for Phase I
- **Validate**: Title non-empty, ID numeric
- **No Need**: SQL escaping, HTML escaping, shell escaping
- **Phase II**: Add SQL injection protection when migrating to SQLite

## Conclusion

**Research Complete**: All architectural questions answered with decisions documented.

**Key Decisions**:
1. Dictionary storage with TaskManager abstraction → Enables Phase II-V migration
2. Sequential integer IDs → Compatible with database auto-increment
3. Tuple return values for errors → Maps to HTTP status codes
4. Dual-layer validation (CLI + service) → Defense in depth
5. Zero external dependencies → Maximizes simplicity

**Next Steps**:
- ✅ Research complete (this document)
- ✅ Data model defined ([data-model.md](data-model.md))
- ✅ Quickstart guide created ([quickstart.md](quickstart.md))
- ✅ ADR-001 documented ([docs/adrs/001-in-memory-to-sqlite-evolution.md](../../docs/adrs/001-in-memory-to-sqlite-evolution.md))
- ⏭️ Proceed to `/sp.tasks` (task generation) after plan approval

**Ready for Task Generation**: All design questions resolved, implementation strategy clear.
