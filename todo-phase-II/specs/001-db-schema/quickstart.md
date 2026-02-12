# Quickstart: Database Schema Setup

**Feature**: 001-db-schema
**Date**: 2026-01-12
**Target Audience**: Backend developers setting up local database

## Prerequisites

- Python 3.11 or higher installed
- Neon Serverless PostgreSQL account ([sign up at neon.tech](https://neon.tech))
- Git repository cloned locally

---

## Step 1: Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install sqlmodel psycopg2-binary alembic python-dotenv pydantic[email]
```

**Dependency Versions**:
- `sqlmodel>=0.0.14` - Combines Pydantic validation + SQLAlchemy ORM
- `psycopg2-binary>=2.9.9` - PostgreSQL database driver
- `alembic>=1.13.1` - Database migration tool
- `python-dotenv>=1.0.0` - Load environment variables from .env
- `pydantic[email]>=2.5.0` - Email validation support

---

## Step 2: Create Neon Database

1. **Sign up for Neon**: Go to [neon.tech](https://neon.tech) and create a free account

2. **Create a new project**:
   - Project name: `todo-app-dev` (or your preferred name)
   - Region: Choose closest to your location
   - PostgreSQL version: 15+ (default)

3. **Get connection string**:
   - Navigate to your project dashboard
   - Click "Connection Details"
   - Copy the connection string (format: `postgresql://user:password@host/database`)
   - **Important**: Neon requires SSL, ensure `?sslmode=require` is appended

**Example connection string**:
```
postgresql://user:AbCdEf123@ep-cool-meadow-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

---

## Step 3: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# backend/.env

# Database connection (from Neon dashboard)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Development settings
ENVIRONMENT=development
DEBUG=True
```

**Security Notes**:
- **NEVER** commit `.env` file to Git
- Add `.env` to `.gitignore` immediately
- Use separate databases for development, staging, and production

**Verify `.gitignore` includes**:
```gitignore
# Environment variables
.env
.env.local
.env.*.local
```

---

## Step 4: Create SQLModel Definitions

Create the database models file:

```bash
# Create directory structure
mkdir -p backend/src/models

# Create models file
touch backend/src/models/__init__.py
touch backend/src/models/user.py
touch backend/src/models/todo.py
```

**File: `backend/src/models/user.py`**
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

**File: `backend/src/models/todo.py`**
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

---

## Step 5: Create Database Connection Module

**File: `backend/src/database.py`**
```python
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Create engine with Neon-optimized settings
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_pre_ping=True,  # Verify connection health
    pool_size=5,  # Small pool for serverless
    max_overflow=10,  # Allow burst connections
    pool_timeout=30,  # Connection wait timeout (seconds)
    pool_recycle=3600,  # Recycle connections after 1 hour
)

def init_db() -> None:
    """
    Initialize database schema (for development/testing only).
    In production, use Alembic migrations instead.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to inject database sessions.

    Usage in FastAPI route:
        @app.get("/")
        def route(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
```

---

## Step 6: Initialize Database Schema

Create an initialization script:

**File: `backend/init_db.py`**
```python
#!/usr/bin/env python3
"""Initialize database schema for development."""

from src.database import init_db, engine
from src.models.user import User
from src.models.todo import Todo

def main():
    print("Creating database schema...")
    print(f"Database URL: {engine.url}")

    # Create all tables
    init_db()

    print("✅ Database schema created successfully!")
    print("\nCreated tables:")
    print("  - user (id, email, hashed_password, created_at, updated_at)")
    print("  - todo (id, title, description, is_completed, user_id, created_at, updated_at)")

if __name__ == "__main__":
    main()
```

**Run the initialization**:
```bash
# Make script executable (Linux/macOS)
chmod +x backend/init_db.py

# Run initialization
python backend/init_db.py
```

**Expected output**:
```
Creating database schema...
Database URL: postgresql://user@host/database
✅ Database schema created successfully!

Created tables:
  - user (id, email, hashed_password, created_at, updated_at)
  - todo (id, title, description, is_completed, user_id, created_at, updated_at)
```

---

## Step 7: Verify Database Schema

Connect to your Neon database to verify tables were created:

### Option 1: Neon Web Console

1. Go to your Neon project dashboard
2. Click "SQL Editor"
3. Run query:
   ```sql
   \dt
   ```
4. You should see `user` and `todo` tables listed

### Option 2: psql CLI

```bash
# Install psql (if not already installed)
# Ubuntu/Debian:
sudo apt-get install postgresql-client

# macOS (via Homebrew):
brew install postgresql

# Connect to database
psql "postgresql://user:password@host/database?sslmode=require"

# List tables
\dt

# Describe user table
\d user

# Describe todo table
\d todo

# Exit
\q
```

**Expected table structures**:
```sql
-- user table
Column         | Type                   | Nullable | Default
---------------+------------------------+----------+-------------------
id             | integer                | not null | nextval('user_id_seq')
email          | character varying(255) | not null |
hashed_password| character varying(255) | not null |
created_at     | timestamp with time zone | not null | now()
updated_at     | timestamp with time zone | not null | now()

Indexes:
    "user_pkey" PRIMARY KEY, btree (id)
    "idx_user_email_unique" UNIQUE, btree (email)

-- todo table
Column        | Type                   | Nullable | Default
--------------+------------------------+----------+-------------------
id            | integer                | not null | nextval('todo_id_seq')
title         | character varying(200) | not null |
description   | text                   |          |
is_completed  | boolean                | not null | false
user_id       | integer                | not null |
created_at    | timestamp with time zone | not null | now()
updated_at    | timestamp with time zone | not null | now()

Indexes:
    "todo_pkey" PRIMARY KEY, btree (id)
    "idx_todo_user_id" btree (user_id)

Foreign-key constraints:
    "todo_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
```

---

## Step 8: Test Database Operations

Create a test script to verify CRUD operations:

**File: `backend/test_db.py`**
```python
#!/usr/bin/env python3
"""Test database operations."""

from sqlmodel import Session
from src.database import engine
from src.models.user import User
from src.models.todo import Todo

def test_user_crud():
    """Test User CRUD operations."""
    with Session(engine) as session:
        # Create user
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"✅ Created user: {user.email} (ID: {user.id})")

        # Read user
        found = session.get(User, user.id)
        assert found.email == "test@example.com"
        print(f"✅ Found user: {found.email}")

        # Create todo for user
        todo = Todo(
            title="Test Todo",
            description="This is a test",
            user_id=user.id
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)
        print(f"✅ Created todo: {todo.title} (ID: {todo.id})")

        # Test cascade delete
        session.delete(user)
        session.commit()
        print(f"✅ Deleted user (cascade deleted todos)")

        # Verify todo was cascade-deleted
        deleted_todo = session.get(Todo, todo.id)
        assert deleted_todo is None
        print(f"✅ Confirmed cascade delete worked")

if __name__ == "__main__":
    try:
        test_user_crud()
        print("\n🎉 All database tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
```

**Run the test**:
```bash
python backend/test_db.py
```

**Expected output**:
```
✅ Created user: test@example.com (ID: 1)
✅ Found user: test@example.com
✅ Created todo: Test Todo (ID: 1)
✅ Deleted user (cascade deleted todos)
✅ Confirmed cascade delete worked

🎉 All database tests passed!
```

---

## Step 9: Setup Alembic for Migrations (Optional but Recommended)

For production, use Alembic to manage schema changes:

```bash
# Initialize Alembic
cd backend
alembic init alembic

# Edit alembic.ini to use DATABASE_URL from environment
# Change line:
#   sqlalchemy.url = driver://user:pass@localhost/dbname
# To:
#   sqlalchemy.url = postgresql://...
# (Or configure in alembic/env.py to read from .env)
```

**File: `backend/alembic/env.py`** (modify to load DATABASE_URL):
```python
from dotenv import load_dotenv
import os

load_dotenv()

# Import SQLModel metadata
from src.models.user import User
from src.models.todo import Todo
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata

# Use DATABASE_URL from environment
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
```

**Generate initial migration**:
```bash
alembic revision --autogenerate -m "Initial schema: User and Todo tables"

# Apply migration
alembic upgrade head
```

---

## Troubleshooting

### Connection Error: "could not connect to server"

**Cause**: Invalid DATABASE_URL or network issue

**Solution**:
1. Verify DATABASE_URL in `.env` is correct (copy from Neon dashboard)
2. Ensure `?sslmode=require` is appended to URL
3. Check Neon project is not paused (free tier pauses after inactivity)

### Error: "relation 'user' already exists"

**Cause**: Running `init_db()` multiple times

**Solution**:
- For development: Drop tables and recreate: `DROP TABLE todo, user CASCADE;`
- For production: Use Alembic migrations instead of `init_db()`

### Import Error: "No module named 'src'"

**Cause**: Python path not configured

**Solution**:
```bash
# Add backend directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Or run scripts with -m flag
python -m src.database
```

### Slow Query Performance

**Cause**: Missing indexes or cold Neon connection

**Solution**:
1. Verify indexes exist: `\d user` and `\d todo` in psql
2. Enable `pool_pre_ping=True` to keep connections warm
3. Check Neon project region matches your location

---

## Next Steps

1. ✅ Database schema created and tested
2. ⬜ Implement FastAPI route handlers (separate feature)
3. ⬜ Add JWT authentication middleware (separate feature)
4. ⬜ Write integration tests for user isolation
5. ⬜ Connect Next.js frontend to backend API

---

## Reference Links

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon Serverless PostgreSQL](https://neon.tech/docs)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Pydantic Email Validation](https://docs.pydantic.dev/latest/api/networks/#pydantic.networks.EmailStr)

---

## File Structure After Setup

```
backend/
├── .env                      # Environment variables (gitignored)
├── alembic/                  # Database migrations (optional)
│   ├── versions/
│   └── env.py
├── src/
│   ├── __init__.py
│   ├── database.py           # Database connection and session
│   └── models/
│       ├── __init__.py
│       ├── user.py           # User SQLModel
│       └── todo.py           # Todo SQLModel
├── init_db.py                # Database initialization script
├── test_db.py                # Database test script
└── requirements.txt          # Python dependencies
```
