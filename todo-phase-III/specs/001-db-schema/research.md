# Research: Database Schema and SQLModel Architecture

**Feature**: 001-db-schema
**Date**: 2026-01-12
**Status**: Completed

## Research Questions

### 1. Primary Key Type: Integer vs UUID

**Decision**: Auto-incrementing Integer (PostgreSQL SERIAL or BIGSERIAL)

**Rationale**:
- **Performance**: Integers are 4-8 bytes vs 16 bytes for UUID, resulting in smaller indexes and faster joins
- **Simplicity**: SERIAL/BIGSERIAL auto-increment eliminates need for client-side ID generation
- **Sequential**: Better for pagination and default ordering by creation time
- **Neon PostgreSQL Support**: Native support for SERIAL types with excellent performance

**Alternatives Considered**:
- **UUID**: Better for distributed systems and prevents ID enumeration attacks, but adds complexity and storage overhead. Not needed for current single-database architecture.
- **Composite Keys**: Unnecessary complexity for this use case

**Implementation**:
```python
# SQLModel definition
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-increment
```

---

### 2. Cascade Behavior for User Deletion

**Decision**: CASCADE on delete (deleting user deletes all their todos)

**Rationale**:
- **Data Consistency**: When a user account is deleted, orphaned todos have no meaning or owner
- **Privacy Compliance**: Complete data removal aligns with GDPR/privacy regulations
- **User Expectation**: Users expect that deleting their account removes all their data
- **Simplicity**: Avoids need for soft-delete patterns or orphan cleanup jobs

**Alternatives Considered**:
- **RESTRICT**: Would prevent user deletion if todos exist, poor UX
- **SET NULL**: Would create orphaned todos with no owner (violates NOT NULL constraint on user_id)
- **Soft Delete**: Adds complexity with `is_deleted` flags, not needed for initial implementation

**Implementation**:
```python
# SQLModel relationship
class Todo(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
```

---

### 3. Connection Pooling for Neon Serverless PostgreSQL

**Decision**: SQLAlchemy pool with serverless-optimized settings

**Rationale**:
- **Cold Starts**: Neon serverless may have cold start latency; pool needs aggressive timeout and retry
- **Connection Limits**: Serverless databases have lower connection limits; keep pool small
- **Connection Reuse**: Pool prevents overhead of repeated connection establishment

**Configuration**:
```python
from sqlalchemy.pool import NullPool  # For serverless environments
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Development only
    pool_pre_ping=True,  # Verify connection before use
    pool_size=5,  # Small pool for serverless
    max_overflow=10,  # Allow burst connections
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=3600,  # Recycle connections after 1 hour
)
```

**Best Practices from Neon Documentation**:
- Use `pool_pre_ping=True` to handle stale connections
- Keep `pool_size` low (5-10) to avoid hitting connection limits
- Set `pool_recycle` to handle Neon's connection recycling
- Consider `NullPool` for AWS Lambda/serverless functions (no connection pooling)

**Alternatives Considered**:
- **NullPool**: No pooling, creates new connection per request. Better for AWS Lambda but unnecessary for long-running FastAPI server
- **Default SQLAlchemy Pool**: Would use larger pool size (20+), wastes connections on serverless

---

### 4. Password Hashing Field Size

**Decision**: `VARCHAR(255)` for hashed_password

**Rationale**:
- **bcrypt Output**: Produces 60-character string (format: `$2b$12$...`)
- **argon2 Output**: Produces ~90-character string
- **Future-Proofing**: 255 characters accommodates future hashing algorithms
- **Storage Efficiency**: VARCHAR only uses actual string length + 1-2 bytes overhead

**Implementation**:
```python
class User(SQLModel, table=True):
    hashed_password: str = Field(max_length=255)
```

**Alternatives Considered**:
- **TEXT**: Unbounded, wastes space and prevents index optimization
- **VARCHAR(60)**: Too tight, prevents migration to stronger algorithms like argon2

---

### 5. Timestamp Handling and Timezone

**Decision**: PostgreSQL `TIMESTAMP WITH TIME ZONE` stored as UTC

**Rationale**:
- **Consistency**: All timestamps stored in single timezone (UTC) prevents conversion errors
- **Global Users**: Application may have users in multiple timezones
- **PostgreSQL Best Practice**: `TIMESTAMPTZ` automatically converts to/from UTC
- **SQLModel/SQLAlchemy**: Python `datetime` objects with `timezone=utc` map cleanly

**Implementation**:
```python
from datetime import datetime, timezone

class User(SQLModel, table=True):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

**Auto-Update Pattern**:
```python
# Use SQLAlchemy `onupdate` for automatic timestamp updates
from sqlalchemy import func

class User(SQLModel, table=True):
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": func.now()}  # Auto-update on modification
    )
```

**Alternatives Considered**:
- **Naive DateTime**: No timezone info, error-prone when comparing across timezones
- **Store as UNIX Timestamp**: Integer milliseconds, loses readability and PostgreSQL date functions

---

### 6. Email Validation Strategy

**Decision**: Pydantic `EmailStr` validation at application layer + database UNIQUE constraint

**Rationale**:
- **Separation of Concerns**: Pydantic validates format before database operation (fail fast)
- **Database Enforces Uniqueness**: UNIQUE constraint prevents race condition on concurrent signups
- **User Feedback**: Application layer provides immediate validation error messages
- **Standard Pattern**: SQLModel integrates Pydantic validation seamlessly

**Implementation**:
```python
from pydantic import EmailStr

class User(SQLModel, table=True):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
```

**Database Level**:
```sql
CREATE UNIQUE INDEX idx_user_email_unique ON user(email);
```

**Alternatives Considered**:
- **Database CHECK Constraint**: PostgreSQL regex-based validation, harder to maintain and provides less friendly error messages
- **Application Only**: Race condition allows duplicate emails if two signups happen simultaneously

---

### 7. Index Strategy

**Decision**: Single-column indexes on foreign keys and frequently queried fields

**Rationale**:
- **Foreign Key Performance**: Index on `Todo.user_id` optimizes `WHERE user_id = ?` queries (most common)
- **Unique Constraint Index**: `User.email` automatically gets index from UNIQUE constraint
- **Avoid Over-Indexing**: Each index adds write overhead; only index frequently queried columns

**Implementation**:
```python
class Todo(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", index=True)  # Explicit index
```

**Query Patterns Optimized**:
- `SELECT * FROM todo WHERE user_id = ?` → Uses index on user_id
- `SELECT * FROM user WHERE email = ?` → Uses unique index on email
- `SELECT * FROM todo WHERE user_id = ? AND is_completed = ?` → May benefit from composite index later

**Alternatives Considered**:
- **Composite Index (user_id, is_completed)**: Premature optimization; single-column index sufficient until proven otherwise by profiling
- **No Indexes**: Terrible performance for user-specific queries on large datasets

---

## Technology Stack Summary

| Component | Choice | Version/Details |
|-----------|--------|-----------------|
| **Language** | Python | 3.11+ |
| **ORM** | SQLModel | Latest (combines Pydantic + SQLAlchemy) |
| **Database** | Neon Serverless PostgreSQL | PostgreSQL 15+ compatible |
| **Migration Tool** | Alembic | Auto-generated from SQLModel models |
| **Connection Pooling** | SQLAlchemy Pool | Serverless-optimized settings |
| **Validation** | Pydantic (via SQLModel) | EmailStr, field constraints |
| **Testing** | pytest + SQLModel fixtures | In-memory SQLite for unit tests |

---

## Dependencies Required

```toml
# pyproject.toml or requirements.txt
sqlmodel = "^0.0.14"  # Pydantic + SQLAlchemy integration
psycopg2-binary = "^2.9.9"  # PostgreSQL driver
alembic = "^1.13.1"  # Database migrations
python-dotenv = "^1.0.0"  # Environment variable loading
pydantic[email] = "^2.5.0"  # EmailStr validation
```

---

## Open Questions for Implementation Phase

1. **Migration Strategy**: Use Alembic for schema migrations or rely on SQLModel's `create_all()` for development?
   - **Recommendation**: Use Alembic from start to support production schema evolution

2. **Test Database**: Use in-memory SQLite for fast unit tests or PostgreSQL for contract tests?
   - **Recommendation**: Both - SQLite for fast unit tests, PostgreSQL testcontainer for integration tests

3. **Database URL Format**: Connection string format for Neon?
   - **Format**: `postgresql://user:password@host/database?sslmode=require`
   - **Note**: Neon requires SSL (`sslmode=require`)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Serverless Cold Start** | First query after idle >5 min may timeout | Use `pool_pre_ping=True`, set aggressive `pool_timeout` |
| **Connection Limit Exceeded** | 429 errors under high load | Keep `pool_size` small (5-10), implement connection retry logic |
| **Migration Failure** | Schema out of sync with code | Use Alembic `revision --autogenerate`, test migrations in staging first |
| **Cascade Delete Accident** | User deletion unintentionally removes data | Implement "Are you sure?" confirmation in API, consider soft-delete for future |

---

## Next Steps (Phase 1)

1. Define SQLModel classes in `data-model.md`
2. Generate API contracts for CRUD operations in `/contracts/`
3. Create `quickstart.md` with setup instructions
4. Update agent context with technology stack
