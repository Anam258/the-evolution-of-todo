# Database Operations Contract

**Feature**: 001-db-schema
**Date**: 2026-01-12
**Type**: Internal Database Layer Contract (not HTTP API)

## Purpose

This document defines the contract for database operations at the SQLModel/SQLAlchemy layer. These are internal Python interfaces that higher layers (API routes, services) will use to interact with the database.

**Note**: This is NOT an HTTP API contract. REST API endpoints will be defined in a separate feature specification.

---

## Database Connection Module

### Connection Configuration

```python
# backend/src/database.py

from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Neon-optimized engine configuration
engine = create_engine(
    DATABASE_URL,
    echo=True,  # SQL logging (disable in production)
    pool_pre_ping=True,  # Verify connection health
    pool_size=5,  # Small pool for serverless
    max_overflow=10,  # Burst capacity
    pool_timeout=30,  # Connection wait timeout (seconds)
    pool_recycle=3600,  # Recycle connections after 1 hour
)

def init_db() -> None:
    """Initialize database schema (development only)."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI to inject database sessions."""
    with Session(engine) as session:
        yield session
```

**Contract**:
- `init_db()`: Creates all tables defined in SQLModel models (for development/testing only)
- `get_session()`: Returns a database session for use in FastAPI dependencies
- Engine configured with Neon-optimized settings (small pool, pre-ping, recycle)

---

## User Operations

### Create User

```python
def create_user(session: Session, email: str, hashed_password: str) -> User:
    """
    Create a new user account.

    Args:
        session: Database session
        email: User email (must be unique)
        hashed_password: Hashed password (never plaintext)

    Returns:
        User: Created user object with generated id

    Raises:
        IntegrityError: If email already exists (UNIQUE constraint violation)
        ValidationError: If email format invalid (Pydantic validation)
    """
    user = User(email=email, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)  # Load generated id and timestamps
    return user
```

**Input Validation**:
- `email`: Must be valid email format (Pydantic `EmailStr`)
- `hashed_password`: Non-empty string, max 255 chars

**Output**:
- Returns `User` object with generated `id`, `created_at`, `updated_at`

**Error Cases**:
- **Duplicate Email**: `sqlalchemy.exc.IntegrityError` (UNIQUE constraint violation)
- **Invalid Email**: `pydantic.ValidationError` (raised before DB operation)

---

### Get User by Email

```python
from typing import Optional

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Retrieve user by email address.

    Args:
        session: Database session
        email: User email to search for

    Returns:
        User | None: User object if found, None otherwise
    """
    return session.query(User).filter(User.email == email).first()
```

**Query Pattern**:
```sql
SELECT * FROM user WHERE email = :email LIMIT 1;
```

**Performance**: O(log N) due to unique index on `email`

**Use Case**: User login (verify email exists, then verify password)

---

### Get User by ID

```python
def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """
    Retrieve user by unique ID.

    Args:
        session: Database session
        user_id: User primary key

    Returns:
        User | None: User object if found, None otherwise
    """
    return session.get(User, user_id)
```

**Query Pattern**:
```sql
SELECT * FROM user WHERE id = :user_id LIMIT 1;
```

**Performance**: O(1) primary key lookup

**Use Case**: Load user profile, verify user existence before creating todo

---

### Delete User

```python
def delete_user(session: Session, user_id: int) -> bool:
    """
    Delete user and all their todos (CASCADE).

    Args:
        session: Database session
        user_id: User primary key

    Returns:
        bool: True if user was deleted, False if user didn't exist

    Side Effects:
        - Deletes all todos owned by user (ON DELETE CASCADE)
    """
    user = session.get(User, user_id)
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True
```

**Cascade Behavior**: Deleting user automatically deletes all `Todo` records with matching `user_id`

**Use Case**: Account deletion (GDPR compliance)

---

## Todo Operations

### Create Todo

```python
def create_todo(
    session: Session,
    title: str,
    user_id: int,
    description: Optional[str] = None
) -> Todo:
    """
    Create a new todo for a user.

    Args:
        session: Database session
        title: Todo title (max 200 chars)
        user_id: Owner's user ID
        description: Optional detailed description

    Returns:
        Todo: Created todo object with generated id

    Raises:
        IntegrityError: If user_id doesn't exist (FOREIGN KEY violation)
        ValidationError: If title exceeds 200 chars
    """
    todo = Todo(
        title=title,
        description=description,
        user_id=user_id,
        is_completed=False  # Default value
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
```

**Input Validation**:
- `title`: Non-empty, max 200 characters
- `user_id`: Must reference existing `user.id`
- `description`: Optional (can be `None`)

**Error Cases**:
- **Invalid user_id**: `sqlalchemy.exc.IntegrityError` (FOREIGN KEY constraint violation)
- **Title too long**: `pydantic.ValidationError`

---

### Get Todos for User

```python
from typing import List

def get_todos_by_user(
    session: Session,
    user_id: int,
    is_completed: Optional[bool] = None
) -> List[Todo]:
    """
    Retrieve all todos for a user, optionally filtered by completion status.

    Args:
        session: Database session
        user_id: Owner's user ID
        is_completed: Filter by completion status (None = all todos)

    Returns:
        List[Todo]: List of todos ordered by created_at (newest first)
    """
    query = session.query(Todo).filter(Todo.user_id == user_id)

    if is_completed is not None:
        query = query.filter(Todo.is_completed == is_completed)

    return query.order_by(Todo.created_at.desc()).all()
```

**Query Patterns**:
- All todos: `SELECT * FROM todo WHERE user_id = :user_id ORDER BY created_at DESC;`
- Completed todos: `SELECT * FROM todo WHERE user_id = :user_id AND is_completed = TRUE ORDER BY created_at DESC;`

**Performance**: O(log N + K) where K = number of user's todos (index on `user_id`)

**User Isolation**: CRITICAL - Always filter by `user_id` to prevent unauthorized access

---

### Get Todo by ID (with User Validation)

```python
def get_todo_by_id(
    session: Session,
    todo_id: int,
    user_id: int
) -> Optional[Todo]:
    """
    Retrieve a specific todo, verifying user ownership.

    Args:
        session: Database session
        todo_id: Todo primary key
        user_id: Owner's user ID (for authorization check)

    Returns:
        Todo | None: Todo object if found and owned by user, None otherwise
    """
    return session.query(Todo).filter(
        Todo.id == todo_id,
        Todo.user_id == user_id  # CRITICAL: User isolation
    ).first()
```

**Query Pattern**:
```sql
SELECT * FROM todo WHERE id = :todo_id AND user_id = :user_id LIMIT 1;
```

**User Isolation**: Returns `None` if todo exists but belongs to another user (prevents enumeration)

**Use Case**: Load todo for update/delete operations (must verify ownership)

---

### Update Todo

```python
def update_todo(
    session: Session,
    todo_id: int,
    user_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_completed: Optional[bool] = None
) -> Optional[Todo]:
    """
    Update a todo's fields, verifying user ownership.

    Args:
        session: Database session
        todo_id: Todo primary key
        user_id: Owner's user ID (for authorization check)
        title: New title (None = no change)
        description: New description (None = no change)
        is_completed: New completion status (None = no change)

    Returns:
        Todo | None: Updated todo if found and owned by user, None otherwise

    Side Effects:
        - Automatically updates `updated_at` timestamp
    """
    todo = get_todo_by_id(session, todo_id, user_id)
    if not todo:
        return None

    if title is not None:
        todo.title = title
    if description is not None:
        todo.description = description
    if is_completed is not None:
        todo.is_completed = is_completed

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
```

**User Isolation**: Uses `get_todo_by_id()` to verify ownership before update

**Timestamp**: `updated_at` auto-updates via database trigger or SQLAlchemy `onupdate`

---

### Delete Todo

```python
def delete_todo(
    session: Session,
    todo_id: int,
    user_id: int
) -> bool:
    """
    Delete a todo, verifying user ownership.

    Args:
        session: Database session
        todo_id: Todo primary key
        user_id: Owner's user ID (for authorization check)

    Returns:
        bool: True if todo was deleted, False if not found or not owned by user
    """
    todo = get_todo_by_id(session, todo_id, user_id)
    if not todo:
        return False

    session.delete(todo)
    session.commit()
    return True
```

**User Isolation**: Verifies ownership before deletion (prevents deleting other users' todos)

---

## Transaction Patterns

### Atomic Operations

```python
def create_user_with_sample_todo(
    session: Session,
    email: str,
    hashed_password: str
) -> tuple[User, Todo]:
    """
    Example: Create user and initial todo in single transaction.

    Args:
        session: Database session
        email: User email
        hashed_password: Hashed password

    Returns:
        (User, Todo): Created user and todo objects

    Raises:
        Exception: Rolls back entire transaction on any error
    """
    try:
        # Create user
        user = User(email=email, hashed_password=hashed_password)
        session.add(user)
        session.flush()  # Get user.id without committing

        # Create sample todo
        todo = Todo(
            title="Welcome! Create your first task",
            user_id=user.id,
            is_completed=False
        )
        session.add(todo)

        session.commit()
        session.refresh(user)
        session.refresh(todo)

        return user, todo
    except Exception:
        session.rollback()
        raise
```

**Pattern**: Use `session.flush()` to get auto-generated IDs mid-transaction

**Error Handling**: Any exception rolls back entire transaction (atomicity)

---

## Error Handling Patterns

### Common Exceptions

```python
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

def safe_create_user(session: Session, email: str, hashed_password: str) -> tuple[Optional[User], Optional[str]]:
    """
    Create user with graceful error handling.

    Returns:
        (User, None): Success
        (None, error_message): Failure with user-friendly message
    """
    try:
        user = create_user(session, email, hashed_password)
        return user, None
    except IntegrityError as e:
        if "unique constraint" in str(e).lower():
            return None, "Email already registered"
        return None, "Database error"
    except ValidationError as e:
        return None, f"Invalid email format: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"
```

**Error Types**:
- `IntegrityError`: Constraint violations (unique, foreign key, not null)
- `ValidationError`: Pydantic validation failures (email format, field types)
- Generic `Exception`: Unexpected errors (log and alert)

---

## Testing Contract

### Unit Test Example

```python
import pytest
from sqlmodel import Session, create_engine, SQLModel

@pytest.fixture
def session():
    """In-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        session.rollback()  # Clean up after each test

def test_create_user(session):
    user = create_user(session, "test@example.com", "hashed_pass")
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.created_at is not None

def test_duplicate_email_fails(session):
    create_user(session, "test@example.com", "pass1")
    with pytest.raises(IntegrityError):
        create_user(session, "test@example.com", "pass2")

def test_user_isolation(session):
    user1 = create_user(session, "user1@example.com", "pass1")
    user2 = create_user(session, "user2@example.com", "pass2")

    todo1 = create_todo(session, "User 1 Todo", user1.id)

    # User 2 should not be able to access User 1's todo
    result = get_todo_by_id(session, todo1.id, user2.id)
    assert result is None  # Returns None due to user_id mismatch

def test_cascade_delete(session):
    user = create_user(session, "test@example.com", "pass")
    todo = create_todo(session, "Test Todo", user.id)

    delete_user(session, user.id)

    # Todo should be cascade-deleted
    result = session.get(Todo, todo.id)
    assert result is None
```

---

## Performance Benchmarks

### Expected Query Times (10k users, 100k todos)

| Operation | Query Time (p95) | Notes |
|-----------|------------------|-------|
| `get_user_by_email()` | <10ms | Unique index on email |
| `get_user_by_id()` | <5ms | Primary key lookup |
| `get_todos_by_user()` | <50ms | Index on user_id, ordered by created_at |
| `create_todo()` | <20ms | Single insert with FK check |
| `update_todo()` | <25ms | Primary key lookup + update |
| `delete_user()` (with cascade) | <100ms | Cascades to N todos (dependent on count) |

**Assumptions**: Neon Serverless PostgreSQL, warm connection pool, single-region latency

---

## Security Checklist

- [ ] All todo queries filter by `user_id` from JWT token
- [ ] Never trust client-provided `user_id` in request bodies
- [ ] Return `None` (not error) when todo exists but user doesn't own it (prevents enumeration)
- [ ] Use parameterized queries (SQLModel handles this automatically)
- [ ] Never log `hashed_password` field
- [ ] Validate email format before database insert
- [ ] Use database transactions for multi-step operations

---

## Next Steps

1. Implement these operations in `backend/src/services/user_service.py` and `backend/src/services/todo_service.py`
2. Write integration tests with PostgreSQL testcontainer
3. Add FastAPI route handlers that call these service functions
4. Implement JWT extraction middleware to get `user_id` for authorization
