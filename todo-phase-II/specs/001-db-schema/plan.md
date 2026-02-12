# Implementation Plan: Database Schema and SQLModel Architecture

**Branch**: `001-db-schema` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-db-schema/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature establishes the foundational data layer for a multi-user todo application using Neon Serverless PostgreSQL with SQLModel ORM. The implementation creates two core entities (User and Todo) with strict user isolation enforced at the database level through foreign key relationships. The schema includes proper indexing for performance, timestamp auditing, and type-safe Python models that combine Pydantic validation with SQLAlchemy ORM capabilities. This foundation enables all subsequent API and authentication features by providing a secure, scalable, and well-structured database layer.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: SQLModel (0.0.14+), SQLAlchemy (2.0+), psycopg2-binary, python-dotenv
**Storage**: Neon Serverless PostgreSQL (cloud-hosted, serverless)
**Testing**: pytest with pytest-asyncio for database integration tests
**Target Platform**: Cross-platform (Windows, Linux, macOS) - backend service
**Project Type**: Web application (backend component)
**Performance Goals**: Query response <100ms for up to 10k todos per user with proper indexing
**Constraints**: Serverless cold start handling, connection pool optimization for Neon
**Scale/Scope**: Initial target: hundreds of users, thousands of todos; schema designed for horizontal scaling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Gate 1: Spec-Driven Excellence
**Status**: PASS
**Evidence**: Feature specification exists at `/specs/001-db-schema/spec.md` with complete user stories, functional requirements, and success criteria. All implementation decisions will be traceable to spec artifacts.

### ✅ Gate 2: Strict User Isolation (NON-NEGOTIABLE)
**Status**: PASS
**Evidence**: Database schema enforces user isolation through:
- Todo table includes `user_id` foreign key (NOT NULL) to User table
- Foreign key constraint prevents orphaned todos
- Index on `user_id` enables efficient user-scoped queries
- Foundation for future API layer to filter all queries by JWT-extracted user_id

### ✅ Gate 3: Modern Architecture
**Status**: PASS
**Evidence**: Backend component of web application architecture:
- SQLModel provides clean separation between data layer and business logic
- Database connection via environment variables (DATABASE_URL)
- Designed for integration with FastAPI (API layer) and Next.js (frontend)
- RESTful API contracts will be defined in Phase 1

### ✅ Gate 4: Type Safety & Code Quality
**Status**: PASS
**Evidence**:
- SQLModel combines Pydantic type validation with SQLAlchemy ORM
- All model fields include Python type hints
- Pydantic validates data before database operations
- No `Any` types in model definitions

### ✅ Gate 5: Authentication & Authorization
**Status**: PASS (Foundation)
**Evidence**: Schema prepared for Better Auth + JWT integration:
- User table includes `hashed_password` field (plaintext passwords prohibited)
- `user_id` foreign key in Todo table enables authorization checks
- Actual JWT validation will be implemented in authentication layer (out of scope)

### ✅ Gate 6: Testing & Validation
**Status**: PASS (Planned)
**Evidence**: Spec includes comprehensive acceptance scenarios:
- Database constraint enforcement tests (unique email, foreign keys, NOT NULL)
- SQLModel validation tests (required fields, type checking)
- Connection establishment tests with valid/invalid DATABASE_URL
- Foundation for future user isolation integration tests

## Project Structure

### Documentation (this feature)

```text
specs/001-db-schema/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── database-schema.sql  # SQL DDL for reference
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLModel definition
│   │   └── todo.py          # Todo SQLModel definition
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py    # Database connection setup with Neon
│   └── config/
│       ├── __init__.py
│       └── settings.py      # Environment variable loading
├── tests/
│   ├── integration/
│   │   ├── test_database_connection.py
│   │   ├── test_user_model.py
│   │   └── test_todo_model.py
│   └── __init__.py
├── .env.example             # Template for environment variables
├── requirements.txt         # Python dependencies
└── README.md               # Setup instructions

frontend/
└── [Not in scope for this feature]
```

**Structure Decision**: Web application structure (Option 2) selected based on constitution requirement for modern architecture with frontend/backend separation. This feature implements the backend data layer foundation. Frontend integration will be addressed in future specifications.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution gates pass:
- Spec-driven approach followed
- User isolation enforced at schema level
- Type-safe SQLModel implementation
- Designed for web architecture integration
- Foundation for authentication and testing requirements

---

## Post-Design Constitution Re-evaluation

*Re-checked after Phase 0 (Research) and Phase 1 (Design) completion*

### ✅ Gate 1: Spec-Driven Excellence
**Status**: PASS ✓
**Post-Design Evidence**:
- `research.md` documents all technology decisions with rationale (Primary key type, cascade behavior, connection pooling, password hashing, timestamps, email validation, indexing)
- `data-model.md` provides complete SQLModel definitions for User and Todo entities with validation rules, relationships, and database schema
- `quickstart.md` provides step-by-step setup instructions for local development
- `contracts/database-operations.md` documents database operations and API contracts
- All design artifacts traceable to functional requirements in `spec.md`

### ✅ Gate 2: Strict User Isolation (NON-NEGOTIABLE)
**Status**: PASS ✓
**Post-Design Evidence**:
- User and Todo entities defined with `user_id` foreign key constraint (`data-model.md:198-200`)
- Index created on `Todo.user_id` for efficient user-scoped queries (`data-model.md:164`)
- Foreign key constraint enforces CASCADE ON DELETE, preventing orphaned todos (`research.md:34`)
- Documentation explicitly states all queries must filter by `user_id` from JWT (`data-model.md:420-422`)
- Security section warns against missing `user_id` filter in queries

### ✅ Gate 3: Modern Architecture
**Status**: PASS ✓
**Post-Design Evidence**:
- SQLModel chosen for type-safe ORM with Pydantic validation (`research.md:10`)
- Neon Serverless PostgreSQL for cloud-hosted, scalable storage (`research.md:56`)
- Environment-based configuration via `.env` file (`quickstart.md:66-78`)
- Connection pooling optimized for serverless architecture (`research.md:66-79`)
- Backend structure prepared for FastAPI integration (`plan.md:89-109`)

### ✅ Gate 4: Type Safety & Code Quality
**Status**: PASS ✓
**Post-Design Evidence**:
- All SQLModel fields use Python type hints: `int`, `str`, `EmailStr`, `bool`, `datetime`, `Optional[T]` (`data-model.md:71-107`)
- Pydantic `EmailStr` validates email format at application layer (`research.md:155`)
- Field constraints enforced: `max_length`, `nullable`, `default`, `unique`, `index` (`data-model.md:82-102`)
- No `Any` types in model definitions
- Validation errors provide clear messages via Pydantic (`data-model.md:165-171`)

### ✅ Gate 5: Authentication & Authorization
**Status**: PASS ✓ (Foundation Ready)
**Post-Design Evidence**:
- User model includes `hashed_password` field (VARCHAR 255) for bcrypt/argon2 (`research.md:95-107`)
- Security section explicitly prohibits plaintext password storage (`data-model.md:426-428`)
- `user_id` foreign key enables JWT-based authorization in future API layer
- Research documents password hashing requirements and field sizing considerations

### ✅ Gate 6: Testing & Validation
**Status**: PASS ✓
**Post-Design Evidence**:
- Testing strategy defined in `data-model.md:363-412`
- Unit tests with SQLite in-memory for fast validation (`data-model.md:367-378`)
- Integration tests planned for constraint enforcement (unique email, foreign keys, CASCADE)
- Test fixtures provided for database session management
- Quickstart includes test script (`quickstart.md:374-432`)

### 📋 Architectural Decisions Requiring Documentation

Based on the three-part test (Impact + Alternatives + Scope), the following significant architectural decisions have been made:

1. **SQLModel ORM Selection** (meets all criteria)
   - **Impact**: Long-term framework choice affecting all database interactions
   - **Alternatives**: Pure SQLAlchemy, Django ORM, Tortoise ORM considered
   - **Scope**: Cross-cutting decision influencing API contracts, validation, and type safety
   - **Documented in**: `research.md:10-28`

2. **Neon Serverless PostgreSQL Platform** (meets all criteria)
   - **Impact**: Infrastructure and deployment strategy
   - **Alternatives**: AWS RDS, Supabase, self-hosted PostgreSQL considered
   - **Scope**: Affects connection pooling, cold start handling, cost model
   - **Documented in**: `research.md:30-53`

3. **Cascade Delete for User → Todo Relationship** (meets all criteria)
   - **Impact**: Data retention policy and user privacy compliance
   - **Alternatives**: RESTRICT, SET NULL, soft-delete patterns considered
   - **Scope**: Affects user deletion workflows and data integrity
   - **Documented in**: `research.md:32-52`

**Recommendation**: Consider documenting these decisions formally via `/sp.adr` command for traceability:
- 📋 `/sp.adr sqlmodel-orm-selection` - Document SQLModel vs alternatives
- 📋 `/sp.adr neon-serverless-postgresql` - Document platform choice and serverless trade-offs
- 📋 `/sp.adr cascade-delete-user-data` - Document data retention and privacy policy

### Final Verdict

**ALL CONSTITUTION GATES PASS** ✅

The database schema and SQLModel architecture design fully complies with all six constitutional principles:
1. ✅ Spec-driven with complete documentation artifacts
2. ✅ User isolation enforced at database level with indexed foreign keys
3. ✅ Modern serverless architecture with type-safe ORM
4. ✅ Full type safety via SQLModel + Pydantic validation
5. ✅ Authentication foundation ready (hashed passwords, user_id relationships)
6. ✅ Testing strategy defined with acceptance scenarios

**No complexity violations or trade-offs requiring justification.**

**Implementation is cleared to proceed to Phase 2: Task Generation** (`/sp.tasks` command)
