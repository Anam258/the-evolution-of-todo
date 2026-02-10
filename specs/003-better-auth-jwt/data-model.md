# Data Model: Authentication System and JWT Integration

**Feature**: 003-better-auth-jwt
**Date**: 2026-01-16
**Status**: Complete

## Overview

This document defines the data models, validation rules, and relationships for the authentication system. The implementation uses SQLModel (Pydantic + SQLAlchemy) for the backend and TypeScript interfaces for the frontend.

---

## Entity Definitions

### User Entity

**Description**: Represents an authenticated user in the system

**SQLModel Definition** (existing in `backend/src/models/user.py`):

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)
    is_active: bool = Field(default=True)

class User(UserBase, table=True):
    """
    User model representing an authenticated user in the system.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str  # Plain text password to be hashed

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
```

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique identifier |
| `email` | String(255) | Unique, Not Null, Indexed | User's email for login |
| `hashed_password` | String(255) | Not Null | BCrypt hashed password |
| `is_active` | Boolean | Default: True | Account activation status |
| `created_at` | DateTime | Default: now() | Account creation timestamp |
| `updated_at` | DateTime | Default: now() | Last modification timestamp |

**Relationships**:
- **One-to-Many**: User → Todos (via `user_id` foreign key in Todo table)

**Validation Rules**:
1. Email must be valid format (Pydantic EmailStr)
2. Email must be unique across all users
3. Password must be at least 8 characters (enforced at API layer)
4. Hashed password uses bcrypt with cost factor 12

---

### JWT Token Structure

**Description**: JSON Web Token format for stateless authentication

**Token Payload Structure**:
```json
{
  "sub": "123",
  "user_id": 123,
  "email": "user@example.com",
  "iat": 1705432800,
  "exp": 1705519200
}
```

**Claims**:
| Claim | Type | Required | Description |
|-------|------|----------|-------------|
| `sub` | String | Yes | Subject - user_id as string (JWT standard) |
| `user_id` | Integer | Yes | User identifier for backward compatibility |
| `email` | String | Yes | User's email address |
| `iat` | Integer | Yes | Issued at (Unix timestamp) |
| `exp` | Integer | Yes | Expiration time (Unix timestamp) |

**Token Generation** (from `backend/src/lib/jwt_utils.py`):
```python
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Configuration**:
| Setting | Value | Environment Variable |
|---------|-------|---------------------|
| Algorithm | HS256 | `JWT_ALGORITHM` |
| Expiration | 24 hours (1440 min) | `JWT_EXPIRATION_DELTA` |
| Secret Key | Min 32 chars | `BETTER_AUTH_SECRET` |

---

### Todo Entity (User Isolation Reference)

**Description**: User-owned resource demonstrating isolation requirements

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique identifier |
| `title` | String(255) | Not Null | Todo title |
| `description` | Text | Nullable | Optional description |
| `completed` | Boolean | Default: False | Completion status |
| `user_id` | Integer | FK → User.id, Not Null, Indexed | Owner reference |
| `created_at` | DateTime | Default: now() | Creation timestamp |
| `updated_at` | DateTime | Default: now() | Last update timestamp |

**Relationships**:
- **Many-to-One**: Todo → User (via `user_id` foreign key)

**Cascade Rules**:
- ON DELETE CASCADE: When user is deleted, all their todos are deleted

**Isolation Enforcement**:
```python
# All todo queries MUST include user_id filter
SELECT * FROM todo WHERE user_id = :authenticated_user_id;

# Never execute queries like this:
# SELECT * FROM todo WHERE id = :todo_id;  # DANGEROUS - no user check
```

---

## API Request/Response Models

### Authentication Request Models

**UserLoginRequest** (Pydantic):
```python
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
```

**UserRegistrationRequest** (Pydantic):
```python
class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
```

### Authentication Response Models

**UserLoginResponse**:
```python
class UserLoginResponse(BaseModel):
    user_id: int
    email: str
    token: str  # JWT token
```

**UserRegistrationResponse**:
```python
class UserRegistrationResponse(BaseModel):
    user_id: int
    email: str
    token: str  # JWT token
```

**API Response Wrapper** (per constitution):
```python
class ApiResponse(BaseModel):
    data: Optional[Dict[str, Any]] = None
    error: Optional[ApiError] = None

class ApiError(BaseModel):
    code: str
    message: str
```

---

## Frontend TypeScript Interfaces

**User Interface**:
```typescript
interface User {
  id: number;
  email: string;
  isActive: boolean;
  createdAt: string;  // ISO 8601
  updatedAt: string;  // ISO 8601
}
```

**AuthResponse Interface**:
```typescript
interface AuthResponse {
  data: {
    user_id: number;
    email: string;
    token: string;
  };
  error?: {
    code: string;
    message: string;
  };
}
```

**JWT Payload Interface**:
```typescript
interface JWTPayload {
  sub: string;
  user_id: number;
  email: string;
  iat: number;
  exp: number;
}
```

---

## Database Schema

**SQL DDL for Reference**:
```sql
-- Users table (already exists from 001-db-schema)
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email ON "user"(email);

-- Todos table (for user isolation demonstration)
CREATE TABLE IF NOT EXISTS todo (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_todo_user_id ON todo(user_id);
```

---

## State Transitions

### User Account States

```
[New] --register--> [Active]
[Active] --deactivate--> [Inactive]
[Inactive] --reactivate--> [Active]
[Active/Inactive] --delete--> [Deleted]
```

### JWT Token States

```
[Generated] --verify--> [Valid] or [Invalid]
[Valid] --time passes--> [Expired]
[Valid] --logout--> [Revoked*]  (* client-side only for MVP)
```

---

## Validation Rules Summary

### User Entity Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| email | Valid email format | "Invalid email format" |
| email | Unique | "User with this email already exists" |
| email | Not empty | "Email is required" |
| password | Min 8 characters | "Password must be at least 8 characters" |
| password | Hashed with bcrypt | (Internal) |

### JWT Validation

| Check | Rule | Error Message |
|-------|------|---------------|
| Signature | Valid with secret | "Invalid or expired token" |
| Expiration | Not expired | "Invalid or expired token" |
| Claims | user_id present | "Invalid token claims" |
| Algorithm | HS256 only | "Invalid or expired token" |

### User Isolation Validation

| Check | Rule | Error Message |
|-------|------|---------------|
| Resource access | user_id matches | 404 "Not found" |
| Query filtering | WHERE user_id = ? | (Enforced at service layer) |

---

## Security Considerations

### Password Handling
- Never store plaintext passwords
- Use bcrypt with cost factor 12+
- Password transmitted over HTTPS only
- Failed login attempts logged (not password)

### Token Security
- Tokens stored in localStorage (XSS mitigated by React)
- Authorization header uses Bearer scheme
- Tokens validated on every protected request
- No sensitive data in token payload (beyond user_id, email)

### User Isolation
- All database queries scoped by user_id
- Service layer enforces user ownership
- 404 returned for non-owned resources (not 403)
- Foreign key constraints prevent orphaned data

---

## Testing Requirements

### Unit Tests
- User model validation (valid/invalid email, password length)
- JWT token creation and verification
- Token expiration handling
- User_id extraction from token

### Integration Tests
- User registration with duplicate email
- Login with correct/incorrect credentials
- Protected endpoint access with valid/invalid/expired tokens
- User isolation: User A cannot access User B's resources

### Security Tests
- SQL injection prevention (parameterized queries)
- Token tampering detection
- Missing/malformed Authorization header handling
- Enumeration attack prevention (404 vs 403)
