# Data Model: Database Schema and SQLModel Architecture

**Feature**: 001-db-schema
**Date**: 2026-01-12
**Status**: Design Complete

## Entity Relationship Diagram

```text
┌─────────────────────────────┐
│          User               │
├─────────────────────────────┤
│ id: int (PK, auto)          │
│ email: str (unique, indexed)│
│ hashed_password: str        │
│ created_at: datetime (UTC)  │
│ updated_at: datetime (UTC)  │
└─────────────────────────────┘
              │
              │ 1:N (one user owns many todos)
              │ ON DELETE CASCADE
              ▼
┌─────────────────────────────┐
│          Todo               │
├─────────────────────────────┤
│ id: int (PK, auto)          │
│ title: str (max 200)        │
│ description: str | None     │
│ is_completed: bool          │
│ user_id: int (FK, indexed)  │
│ created_at: datetime (UTC)  │
│ updated_at: datetime (UTC)  │
└─────────────────────────────┘
```

---

## Entity: User

**Purpose**: Represents an authenticated user account with unique email identifier.

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | `int` | PRIMARY KEY, AUTO INCREMENT | Auto-generated | Unique user identifier |
| `email` | `EmailStr` | UNIQUE, NOT NULL, INDEXED, MAX 255 | - | User's email address (login identifier) |
| `hashed_password` | `str` | NOT NULL, MAX 255 | - | bcrypt/argon2 hashed password (never plaintext) |
| `created_at` | `datetime` | NOT NULL, TIMEZONE UTC | `now()` | Account creation timestamp |
| `updated_at` | `datetime` | NOT NULL, TIMEZONE UTC | `now()` | Last modification timestamp (auto-updates) |

### Relationships

- **todos**: One-to-Many relationship with `Todo` entity
  - Accessible via `user.todos` (SQLModel relationship)
  - Cascade delete: Deleting user deletes all their todos

### Indexes

- **PRIMARY KEY**: `id` (implicit, clustered)
- **UNIQUE INDEX**: `idx_user_email_unique` on `email` (for fast login lookups)

### Validation Rules

- **email**: Must be valid email format (enforced by Pydantic `EmailStr`)
- **hashed_password**: Non-empty string (frontend must never send plaintext password)
- **created_at / updated_at**: Must be timezone-aware datetime (UTC)

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime, timezone
from typing import Optional, List

class User(SQLModel, table=True):
    """User account model with authentication credentials."""

    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(
        unique=True,
        index=True,
        max_length=255,
        sa_column_kwargs={"nullable": False}
    )
    hashed_password: str = Field(
        max_length=255,
        sa_column_kwargs={"nullable": False}
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"nullable": False}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "nullable": False,
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )

    # Relationships
    todos: List["Todo"] = Relationship(back_populates="owner", cascade_delete=True)
```

### Database Schema (PostgreSQL)

```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_user_email_unique ON user(email);

-- Trigger for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_updated_at BEFORE UPDATE ON user
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Entity: Todo

**Purpose**: Represents a task or todo item owned by a specific user.

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | `int` | PRIMARY KEY, AUTO INCREMENT | Auto-generated | Unique todo identifier |
| `title` | `str` | NOT NULL, MAX 200 | - | Short task description |
| `description` | `str \| None` | NULLABLE, TEXT | `None` | Optional detailed description |
| `is_completed` | `bool` | NOT NULL | `False` | Task completion status |
| `user_id` | `int` | FOREIGN KEY (user.id), NOT NULL, INDEXED | - | Owner of this todo (foreign key to User) |
| `created_at` | `datetime` | NOT NULL, TIMEZONE UTC | `now()` | Todo creation timestamp |
| `updated_at` | `datetime` | NOT NULL, TIMEZONE UTC | `now()` | Last modification timestamp (auto-updates) |

### Relationships

- **owner**: Many-to-One relationship with `User` entity
  - Accessible via `todo.owner` (SQLModel relationship)
  - Foreign key constraint: `user_id` must reference existing `user.id`
  - ON DELETE CASCADE: Deleting parent user deletes this todo

### Indexes

- **PRIMARY KEY**: `id` (implicit, clustered)
- **FOREIGN KEY INDEX**: `idx_todo_user_id` on `user_id` (optimizes user-specific queries)

### Validation Rules

- **title**: Non-empty string, max 200 characters (enforced by SQLModel Field)
- **description**: Optional text (can be `None` or empty string)
- **is_completed**: Boolean only (true/false, not nullable)
- **user_id**: Must reference existing user (enforced by foreign key constraint)

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import Optional

class Todo(SQLModel, table=True):
    """Todo task model with user ownership."""

    __tablename__ = "todo"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(
        max_length=200,
        sa_column_kwargs={"nullable": False}
    )
    description: Optional[str] = Field(
        default=None,
        sa_column_kwargs={"nullable": True}
    )
    is_completed: bool = Field(
        default=False,
        sa_column_kwargs={"nullable": False}
    )
    user_id: int = Field(
        foreign_key="user.id",
        index=True,
        sa_column_kwargs={"nullable": False, "ondelete": "CASCADE"}
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"nullable": False}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "nullable": False,
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )

    # Relationships
    owner: Optional["User"] = Relationship(back_populates="todos")
```

### Database Schema (PostgreSQL)

```sql
CREATE TABLE todo (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_todo_user_id ON todo(user_id);

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_todo_updated_at BEFORE UPDATE ON todo
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Data Integrity Constraints

### Foreign Key Constraints

1. **Todo.user_id → User.id**
   - **Constraint**: `FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE`
   - **Enforcement**: Database-level constraint prevents orphaned todos
   - **Cascade Behavior**: Deleting a user automatically deletes all their todos
   - **User Isolation**: Ensures every todo belongs to exactly one user

### Unique Constraints

1. **User.email**
   - **Constraint**: `UNIQUE INDEX idx_user_email_unique`
   - **Enforcement**: Database prevents duplicate email registrations
   - **Race Condition Handling**: Atomic uniqueness check prevents concurrent signup conflicts

### Check Constraints

1. **User.email**
   - **Application-Level**: Pydantic `EmailStr` validates format before database operation
   - **Pattern**: Must match standard email regex (handled by Pydantic)

2. **Todo.title**
   - **Constraint**: Non-empty string, max 200 characters
   - **Enforcement**: SQLModel Field validation + PostgreSQL VARCHAR(200)

---

## State Transitions

### User Entity

```text
[No Account] --signup--> [Active User] --delete account--> [Deleted] (CASCADE deletes todos)
```

**State Rules**:
- User cannot change email after creation (requires new account)
- User can update password (via hashed_password field)
- User deletion is permanent and cascades to todos

### Todo Entity

```text
[Not Created] --create--> [Incomplete] --mark complete--> [Completed] --mark incomplete--> [Incomplete]
                                  │
                                  └--delete--> [Deleted]
```

**State Rules**:
- Todo can toggle `is_completed` state freely
- Todo cannot change owner (`user_id` immutable after creation)
- Todo deletion is permanent (no soft-delete in this phase)

---

## Performance Considerations

### Query Patterns

1. **Fetch all todos for a user**:
   ```sql
   SELECT * FROM todo WHERE user_id = ? ORDER BY created_at DESC;
   ```
   - **Optimization**: Index on `user_id` (defined as `idx_todo_user_id`)
   - **Expected Performance**: O(log N) index lookup + O(K) result scan (K = user's todo count)

2. **User login by email**:
   ```sql
   SELECT * FROM user WHERE email = ?;
   ```
   - **Optimization**: Unique index on `email` (defined as `idx_user_email_unique`)
   - **Expected Performance**: O(log N) index lookup (single row)

3. **Filter completed todos for user**:
   ```sql
   SELECT * FROM todo WHERE user_id = ? AND is_completed = TRUE;
   ```
   - **Optimization**: Uses `user_id` index, then filters in-memory
   - **Future Optimization**: Composite index `(user_id, is_completed)` if this query becomes frequent

### Index Strategy

- **Single-Column Indexes**: Sufficient for current requirements (user_id, email)
- **Avoid Over-Indexing**: Each index adds write overhead (~10-15% per index)
- **Future Consideration**: Add composite index `(user_id, is_completed)` only if profiling shows need

---

## Migration Strategy

### Initial Schema Creation

```python
# Using SQLModel's create_all() for development
from sqlmodel import SQLModel, create_engine

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)  # Creates all tables
```

### Production Migrations (Alembic)

```bash
# Generate migration from SQLModel models
alembic revision --autogenerate -m "Initial schema: User and Todo tables"

# Apply migration
alembic upgrade head
```

**Migration File Structure**:
```
alembic/
├── versions/
│   └── 001_initial_schema.py
├── env.py
└── alembic.ini
```

---

## Testing Data Models

### Unit Tests (SQLite In-Memory)

```python
import pytest
from sqlmodel import Session, create_engine, SQLModel
from datetime import datetime, timezone

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_user_creation(session):
    user = User(email="test@example.com", hashed_password="hashed123")
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.created_at is not None

def test_todo_requires_user(session):
    # Should fail without valid user_id (foreign key constraint)
    with pytest.raises(Exception):
        todo = Todo(title="Test", user_id=999)
        session.add(todo)
        session.commit()

def test_cascade_delete(session):
    user = User(email="test@example.com", hashed_password="hashed123")
    session.add(user)
    session.commit()

    todo = Todo(title="Test Todo", user_id=user.id)
    session.add(todo)
    session.commit()

    # Delete user should cascade to todo
    session.delete(user)
    session.commit()

    # Todo should be gone
    result = session.query(Todo).filter(Todo.id == todo.id).first()
    assert result is None
```

---

## Security Considerations

### User Isolation

- **Critical**: All queries for Todo must filter by `user_id` from JWT token
- **Pattern**: `SELECT * FROM todo WHERE user_id = :user_id AND id = :todo_id`
- **Never**: `SELECT * FROM todo WHERE id = :todo_id` (missing user_id filter allows unauthorized access)

### Password Storage

- **NEVER** store plaintext passwords in `hashed_password` field
- **ALWAYS** hash with bcrypt, argon2, or similar before insertion
- **Validation**: Application layer must enforce password complexity rules before hashing

### Email Privacy

- **Index on email**: Necessary for login performance, but reveals email existence via timing attacks
- **Mitigation**: Generic error messages ("Invalid email or password") prevent user enumeration

---

## Open Questions for Implementation

1. **Should updated_at trigger be database-level or application-level?**
   - **Recommendation**: Database-level trigger (shown above) ensures consistency even for direct SQL updates

2. **Should we add `deleted_at` for soft-delete pattern?**
   - **Decision**: Out of scope for Phase 2. Hard delete with CASCADE is sufficient for MVP.

3. **Should Todo.title be full-text searchable?**
   - **Decision**: Not required for current spec. Can add GIN index on `to_tsvector(title)` later if needed.

---

## Next Steps

1. Generate API contracts for CRUD operations (see `/contracts/` directory)
2. Create database connection module with Neon-optimized settings
3. Write integration tests for foreign key constraints and cascade behavior
4. Document quickstart guide for local development setup
