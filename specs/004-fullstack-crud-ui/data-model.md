# Data Model: Task Management for Todo Application

**Feature**: 004-fullstack-crud-ui
**Date**: 2026-01-15
**Author**: claude

## 1. Entity: Task

### 1.1 Fields
- **id** (UUID, Primary Key)
  - Purpose: Unique identifier for each task
  - Type: UUID
  - Constraints: Auto-generated, not nullable, primary key
  - Default: uuid.uuid4()

- **title** (String)
  - Purpose: Title or subject of the task
  - Type: String (max_length=255)
  - Constraints: Not nullable, min_length=1
  - Validation: Required field, must be 1-255 characters

- **description** (String, Optional)
  - Purpose: Detailed description of the task
  - Type: String (max_length=1000, nullable=True)
  - Constraints: Nullable, optional field
  - Validation: Max 1000 characters if provided

- **is_completed** (Boolean)
  - Purpose: Completion status of the task
  - Type: Boolean
  - Constraints: Not nullable
  - Default: False

- **created_at** (DateTime)
  - Purpose: Timestamp when the task was created
  - Type: DateTime
  - Constraints: Not nullable
  - Default: datetime.utcnow()

- **updated_at** (DateTime)
  - Purpose: Timestamp when the task was last updated
  - Type: DateTime
  - Constraints: Not nullable
  - Default: datetime.utcnow()
  - On Update: Automatically updated when record is modified

- **user_id** (Integer, Foreign Key)
  - Purpose: Reference to the user who owns this task
  - Type: Integer
  - Constraints: Not nullable, foreign key to User.id, ondelete="CASCADE"
  - Relationship: Links to User model for user isolation

### 1.2 Relationships
- **user** (Relationship to User model)
  - Type: Optional[User]
  - Back Reference: Back-populates "tasks" on User model
  - Purpose: Optional relationship to access user details if needed

### 1.3 Validation Rules
- Title must be 1-255 characters
- Description, if provided, must be ≤ 1000 characters
- user_id must reference an existing user
- is_completed defaults to False
- created_at and updated_at are automatically managed

## 2. SQLModel Definition

```python
from uuid import uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import uuid

class TaskBase(SQLModel):
    """Base model containing common fields for Task"""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    """Task model with all fields and relationships"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")

    # Relationship to user (optional)
    user: Optional["User"] = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    """Model for creating new tasks"""
    pass

class TaskRead(TaskBase):
    """Model for reading task data"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    user_id: int

class TaskUpdate(SQLModel):
    """Model for updating existing tasks"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: Optional[bool] = None

class TaskPatch(SQLModel):
    """Model for patching task status"""
    is_completed: bool
```

## 3. Indexes and Performance

### 3.1 Required Indexes
- **Primary Key Index**: On `id` (automatically created)
- **Foreign Key Index**: On `user_id` (essential for user isolation queries)
- **Composite Index**: On `(user_id, created_at)` for efficient user task retrieval with ordering

### 3.2 Query Patterns
- Retrieve all tasks for a specific user (filtered by user_id)
- Retrieve completed vs incomplete tasks for a user
- Sort tasks by creation date
- Update task completion status

## 4. User Isolation Mechanism

### 4.1 Database-Level Enforcement
- All task queries must include WHERE clause filtering by user_id
- Foreign key constraint ensures referential integrity
- CASCADE delete removes tasks when user is deleted

### 4.2 Application-Level Enforcement
- Authentication middleware extracts user_id from JWT
- All API endpoints automatically filter by authenticated user's tasks
- 404 responses for attempts to access non-owned resources (prevents enumeration)

## 5. State Transitions

### 5.1 Task Lifecycle
```
CREATED (is_completed=False)
    ↓
COMPLETED (is_completed=True)
    ↓
MODIFIED (can toggle is_completed back to False)
```

### 5.2 Valid Transitions
- New Task → Active Task (is_completed=False)
- Active Task → Completed Task (is_completed=True)
- Completed Task → Active Task (is_completed=False)
- Any State → Deleted (record removed from database)

## 6. Data Integrity Constraints

### 6.1 Referential Integrity
- Task.user_id must reference an existing User.id
- On User deletion, all associated Tasks are automatically deleted (CASCADE)

### 6.2 Business Logic Constraints
- A task cannot be completed if it's already deleted
- Task titles must be non-empty strings
- Only the owner of a task can modify it

## 7. API Representation

### 7.1 JSON Structure
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project proposal",
  "description": "Finish the project proposal document and submit for review",
  "is_completed": false,
  "created_at": "2023-10-15T10:30:00Z",
  "updated_at": "2023-10-15T10:30:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 7.2 API Models
- **TaskCreate**: title, description (optional)
- **TaskRead**: All fields including id, timestamps, and user_id
- **TaskUpdate**: All fields optional for full updates
- **TaskPatch**: Only is_completed for status updates