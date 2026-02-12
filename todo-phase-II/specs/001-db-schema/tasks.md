# Tasks: Database Schema and SQLModel Architecture

**Input**: Design documents from `/specs/001-db-schema/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Integration tests included per spec acceptance scenarios

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Per plan.md: Web application structure with `backend/` directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md (backend/src/models/, backend/src/database/, backend/src/config/, backend/tests/integration/)
- [x] T002 Create backend/requirements.txt with dependencies: sqlmodel==0.0.14, sqlalchemy==2.0.25, psycopg2-binary==2.9.9, pydantic==2.5.0, pydantic-settings==2.1.0, python-dotenv==1.0.0, pytest==7.4.3, pytest-asyncio==0.21.1
- [x] T003 [P] Create backend/.env.example with DATABASE_URL template and security notes from quickstart.md
- [x] T004 [P] Create backend/.gitignore to exclude .env, .env.local, __pycache__, *.pyc, venv/
- [x] T005 [P] Create backend/src/__init__.py as empty file for package structure
- [x] T006 [P] Create backend/src/models/__init__.py as empty file for models package
- [x] T007 [P] Create backend/src/database/__init__.py as empty file for database package
- [x] T008 [P] Create backend/src/config/__init__.py as empty file for config package
- [x] T009 [P] Create backend/tests/__init__.py as empty file for tests package
- [x] T010 [P] Create backend/tests/integration/__init__.py as empty file for integration tests package

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Create backend/src/config/settings.py with Pydantic BaseSettings to load DATABASE_URL from environment per research.md:155-165
- [ ] T012 Create backend/src/database/connection.py with SQLAlchemy engine using serverless-optimized connection pool settings per research.md:66-79

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 3 - System Connects to Neon Database (Priority: P1) 🎯 MVP Foundation

**Goal**: Establish secure database connection to Neon Serverless PostgreSQL using environment variables, with proper connection pooling for serverless architecture

**Independent Test**: Load DATABASE_URL from .env file, initialize connection, execute SELECT 1 query, verify successful connection with proper error handling for invalid URLs and cold starts

### Integration Tests for User Story 3

- [ ] T013 [US3] Create backend/tests/integration/test_database_connection.py with test_valid_database_url_connects_successfully per spec.md acceptance scenario 1
- [ ] T014 [US3] Add test_simple_query_executes_after_connection to test_database_connection.py per spec.md acceptance scenario 2
- [ ] T015 [US3] Add test_invalid_database_url_logs_clear_error to test_database_connection.py per spec.md acceptance scenario 3
- [ ] T016 [US3] Add test_connection_pool_handles_serverless_cold_start to test_database_connection.py per spec.md acceptance scenario 4

### Implementation for User Story 3

- [ ] T017 [US3] Implement get_session() generator function in backend/src/database/connection.py for FastAPI dependency injection per data-model.md:230-241
- [ ] T018 [US3] Implement init_db() function in backend/src/database/connection.py to create schema using SQLModel.metadata.create_all() per data-model.md:223-228
- [ ] T019 [US3] Add connection health check and error handling to backend/src/database/connection.py with clear error messages when DATABASE_URL missing
- [ ] T020 [US3] Create backend/init_db.py script to initialize database schema for development per quickstart.md:249-272
- [ ] T021 [US3] Run integration tests for User Story 3 to verify all acceptance scenarios pass

**Checkpoint**: Database connection working - schema creation can now proceed

---

## Phase 4: User Story 1 - Database Administrator Provisions Schema (Priority: P1) 🎯 MVP Core

**Goal**: Provision multi-user todo application database schema with User and Todo tables, enforcing user data isolation through foreign key constraints, unique indexes, and CASCADE delete behavior

**Independent Test**: Run database migrations on empty Neon database, verify table creation with correct columns/constraints/indexes, test unique email constraint, test foreign key relationships, test CASCADE delete behavior

### Integration Tests for User Story 1

- [ ] T022 [P] [US1] Create backend/tests/integration/test_user_model.py with test_user_table_created_with_all_columns per spec.md acceptance scenario 1
- [ ] T023 [P] [US1] Add test_duplicate_email_fails_unique_constraint to test_user_model.py per spec.md acceptance scenario 2
- [ ] T024 [P] [US1] Add test_user_email_index_exists to test_user_model.py to verify idx_user_email_unique per data-model.md:61
- [ ] T025 [P] [US1] Create backend/tests/integration/test_todo_model.py with test_todo_table_created_with_all_columns per spec.md acceptance scenario 1
- [ ] T026 [P] [US1] Add test_todo_foreign_key_relationship_established to test_todo_model.py per spec.md acceptance scenario 3
- [ ] T027 [P] [US1] Add test_user_deletion_cascades_to_todos to test_todo_model.py per spec.md acceptance scenario 4 and data-model.md:396-411
- [ ] T028 [P] [US1] Add test_todo_user_id_index_exists to test_todo_model.py to verify idx_todo_user_id per data-model.md:163

### Implementation for User Story 1

- [ ] T029 [P] [US1] Create backend/src/models/user.py with User SQLModel class per data-model.md:71-107 including id, email (EmailStr, unique, indexed), hashed_password (max 255), created_at (UTC default), updated_at (UTC auto-update), and todos relationship
- [ ] T030 [P] [US1] Create backend/src/models/todo.py with Todo SQLModel class per data-model.md:174-216 including id, title (max 200), description (optional), is_completed (default False), user_id (foreign key with CASCADE), created_at, updated_at, and owner relationship
- [ ] T031 [US1] Update backend/src/models/__init__.py to export User and Todo classes for easy imports
- [ ] T032 [US1] Run backend/init_db.py script to create User and Todo tables on Neon database
- [ ] T033 [US1] Verify schema creation by connecting to Neon SQL Editor and running \dt to list tables, \d user to describe User table structure, \d todo to describe Todo table structure per quickstart.md:296-368
- [ ] T034 [US1] Run integration tests for User Story 1 to verify all acceptance scenarios pass (constraints, indexes, CASCADE)

**Checkpoint**: Database schema provisioned and validated - SQLModel integration testing can now proceed

---

## Phase 5: User Story 2 - Backend Developer Integrates SQLModel (Priority: P2)

**Goal**: Validate SQLModel classes provide type-safe database operations with Pydantic validation, enabling backend developers to perform CRUD operations with confidence that data integrity is enforced at the Python layer

**Independent Test**: Import SQLModel classes, instantiate with valid data and verify success, instantiate with invalid data and verify Pydantic ValidationError, access User.todos relationship and verify it's properly defined

### Integration Tests for User Story 2

- [ ] T035 [P] [US2] Create backend/tests/integration/test_user_validation.py with test_user_instantiation_with_valid_data_succeeds per spec.md acceptance scenario 1
- [ ] T036 [P] [US2] Add test_user_missing_required_field_raises_validation_error to test_user_validation.py per spec.md acceptance scenario 4
- [ ] T037 [P] [US2] Add test_user_invalid_email_format_raises_validation_error to test_user_validation.py to verify EmailStr validation per data-model.md:65
- [ ] T038 [P] [US2] Add test_user_hashed_password_field_validation to test_user_validation.py to ensure non-empty per data-model.md:66
- [ ] T039 [P] [US2] Create backend/tests/integration/test_todo_validation.py with test_todo_instantiation_with_valid_data_succeeds per spec.md acceptance scenario 2
- [ ] T040 [P] [US2] Add test_todo_missing_required_field_raises_validation_error to test_todo_validation.py per spec.md acceptance scenario 4
- [ ] T041 [P] [US2] Add test_todo_title_max_length_validation to test_todo_validation.py to verify 200 char limit per data-model.md:167
- [ ] T042 [P] [US2] Add test_todo_invalid_user_id_fails_foreign_key to test_todo_validation.py per edge case in spec.md:63
- [ ] T043 [US2] Create backend/tests/integration/test_relationships.py with test_user_todos_relationship_defined per spec.md acceptance scenario 3
- [ ] T044 [US2] Add test_todo_owner_relationship_defined to test_relationships.py to verify many-to-one relationship per data-model.md:155-158

### Implementation for User Story 2

- [ ] T045 [US2] Create backend/test_db.py integration script per quickstart.md:374-432 to demonstrate CRUD operations with both User and Todo models
- [ ] T046 [US2] Run backend/test_db.py to verify User creation, Todo creation with foreign key, cascade delete, and relationship access
- [ ] T047 [US2] Run all integration tests for User Story 2 to verify Pydantic validation catches invalid data before database operations
- [ ] T048 [US2] Document SQLModel validation behavior in backend/README.md including examples of valid/invalid instantiation and Pydantic error messages

**Checkpoint**: SQLModel integration validated - backend developers can confidently use type-safe models for database operations

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation across all user stories

- [ ] T049 [P] Create backend/README.md with setup instructions from quickstart.md (dependencies, Neon setup, environment variables, schema initialization, testing)
- [ ] T050 [P] Verify backend/.env.example includes all required variables with security notes from quickstart.md:66-91
- [ ] T051 Run complete test suite across all user stories: pytest backend/tests/integration/ -v
- [ ] T052 Validate quickstart.md instructions work on fresh environment by following steps 1-8
- [ ] T053 [P] Add troubleshooting section to backend/README.md with common errors from quickstart.md:497-537
- [ ] T054 [P] Document connection pooling configuration in backend/README.md with serverless best practices from research.md:56-90

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T010) completion - BLOCKS all user stories
- **User Story 3 (Phase 3)**: Depends on Foundational (T011-T012) - Connection foundation
- **User Story 1 (Phase 4)**: Depends on User Story 3 (T013-T021) - Schema needs working connection
- **User Story 2 (Phase 5)**: Depends on User Story 1 (T022-T034) - Validation tests need existing models
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 3 (P1)**: Can start after Foundational phase - No dependencies on other stories
- **User Story 1 (P1)**: Depends on User Story 3 (working database connection) - Cannot provision schema without connection
- **User Story 2 (P2)**: Depends on User Story 1 (User and Todo models must exist) - Cannot test validation without models

### Within Each User Story

- Tests can be written first (T013-T016, T022-T028, T035-T044) before implementation
- Models (T029-T030) can run in parallel [P]
- Schema creation (T032) depends on models being defined (T029-T031)
- Validation tests (US2) depend on models from US1 being complete

### Parallel Opportunities

- **Phase 1 Setup**: T003-T010 all marked [P] - can create files simultaneously
- **Phase 2 Foundational**: T011-T012 can run in parallel (different files)
- **User Story 3 Tests**: T013-T016 can run in parallel [no explicit [P] as they're in same file but logically independent test functions]
- **User Story 1 Tests**: T022-T028 all marked [P] - different test files
- **User Story 1 Models**: T029-T030 marked [P] - can create User and Todo models simultaneously
- **User Story 2 Tests**: T035-T044 all marked [P] - different test files
- **Polish**: T049-T050, T053-T054 marked [P] - documentation tasks

---

## Parallel Example: User Story 1

```bash
# Launch all integration tests for User Story 1 together:
Task T022: "Create test_user_model.py with test_user_table_created_with_all_columns"
Task T023: "Add test_duplicate_email_fails_unique_constraint to test_user_model.py"
Task T024: "Add test_user_email_index_exists to test_user_model.py"
Task T025: "Create test_todo_model.py with test_todo_table_created_with_all_columns"
Task T026: "Add test_todo_foreign_key_relationship_established to test_todo_model.py"
Task T027: "Add test_user_deletion_cascades_to_todos to test_todo_model.py"
Task T028: "Add test_todo_user_id_index_exists to test_todo_model.py"

# Launch both models together after tests:
Task T029: "Create user.py with User SQLModel class"
Task T030: "Create todo.py with Todo SQLModel class"
```

---

## Implementation Strategy

### MVP First (User Story 3 + User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010) → Project structure ready
2. Complete Phase 2: Foundational (T011-T012) → Config and connection infrastructure ready
3. Complete Phase 3: User Story 3 (T013-T021) → Database connection working
4. Complete Phase 4: User Story 1 (T022-T034) → Schema provisioned and validated
5. **STOP and VALIDATE**: Test database schema independently with Neon SQL Editor
6. MVP Database Layer Complete - Ready for API layer development

### Incremental Delivery

1. Complete Setup + Foundational → Infrastructure ready
2. Add User Story 3 → Test connection independently → Database accessible
3. Add User Story 1 → Test schema independently → Database schema ready for API
4. Add User Story 2 → Test validation independently → Type-safe models validated
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (T001-T010) together
2. Team completes Foundational (T011-T012) together
3. Once Foundational done:
   - Developer A: User Story 3 (T013-T021) - Connection
   - Developer B: Can prepare User Story 1 tests (T022-T028) while waiting
4. After US3 complete:
   - Developer A: User Story 1 implementation (T029-T034)
   - Developer B: User Story 2 tests preparation (T035-T044)
5. After US1 complete:
   - Developer A or B: User Story 2 implementation (T045-T048)

---

## Task Summary

- **Total Tasks**: 54
- **Phase 1 (Setup)**: 10 tasks (T001-T010) - All parallelizable except T001
- **Phase 2 (Foundational)**: 2 tasks (T011-T012) - Both parallelizable
- **Phase 3 (User Story 3)**: 9 tasks (T013-T021) - 4 tests + 5 implementation
- **Phase 4 (User Story 1)**: 13 tasks (T022-T034) - 7 tests [P] + 6 implementation, 2 models [P]
- **Phase 5 (User Story 2)**: 14 tasks (T035-T048) - 10 tests [P] + 4 implementation
- **Phase 6 (Polish)**: 6 tasks (T049-T054) - 4 documentation [P] + 2 validation

**Parallel Opportunities**: 32 tasks marked [P] across all phases

**MVP Scope** (Recommended): Phase 1-4 (T001-T034) = 34 tasks → Complete database schema foundation

**Full Feature**: All 54 tasks → Complete database layer with validated type-safe models

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [US1], [US2], [US3] labels map tasks to user stories from spec.md
- Each user story independently testable at checkpoint
- Tests reference specific acceptance scenarios from spec.md
- File paths follow plan.md web application structure (backend/)
- All SQLModel code references data-model.md line numbers for traceability
- Connection pooling settings reference research.md decisions
- Quickstart validation ensures documentation accuracy
