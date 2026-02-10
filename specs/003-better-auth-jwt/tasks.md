# Tasks: Authentication System and JWT Integration

**Feature**: 003-better-auth-jwt
**Branch**: `003-better-auth-jwt` | **Date**: 2026-01-16
**Input**: Design documents from `/specs/003-better-auth-jwt/`
**Prerequisites**: plan.md (complete), spec.md (complete), data-model.md (complete), contracts/auth-api.yaml (complete)

**Tests**: Tests are included as the spec mentions comprehensive acceptance scenarios and constitution requires testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend uses Python 3.11+ with FastAPI, SQLModel
- Frontend uses Next.js with TypeScript

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing project structure and add any missing configuration

- [x] T001 Verify backend project structure matches plan.md layout in backend/src/
- [x] T002 Verify frontend project structure matches plan.md layout in frontend/src/
- [x] T003 [P] Create backend/.env.example with BETTER_AUTH_SECRET and DATABASE_URL templates
- [x] T004 [P] Create frontend/.env.local.example with NEXT_PUBLIC_API_URL template
- [x] T005 [P] Verify python-jose and passlib[bcrypt] are in backend/requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Implement auth configuration validation in backend/src/config/auth_config.py (check BETTER_AUTH_SECRET on startup)
- [x] T007 [P] Verify User model with email, hashed_password, is_active fields in backend/src/models/user.py
- [x] T008 [P] Verify jwt_utils with create_access_token, verify_token functions in backend/src/lib/jwt_utils.py
- [x] T009 Implement password hashing service using bcrypt in backend/src/services/auth_service.py
- [x] T010 Verify database connection and User table exists via backend/src/database/connection.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Backend Verifies JWT and Enforces User Isolation (Priority: P1) 🎯 MVP

**Goal**: FastAPI middleware verifies JWT tokens on every protected request and automatically extracts the authenticated user_id, ensuring all database queries are scoped to the authenticated user

**Independent Test**: Send requests with valid JWTs, invalid JWTs, and missing JWTs to protected endpoints. Verify valid tokens pass through with extracted user_id, invalid tokens return 401, and database queries automatically filter by user_id.

**User Story Reference**: User Story 1 from spec.md (P1 - Security Foundation)

### Tests for User Story 1

- [x] T011 [P] [US1] Create middleware unit tests for valid/invalid/missing JWT in backend/tests/test_auth_middleware.py
- [x] T012 [P] [US1] Create user isolation tests (User A cannot access User B's data) in backend/tests/test_user_isolation.py

### Implementation for User Story 1

- [x] T013 [US1] Implement JWT verification middleware with HTTPBearer in backend/src/middleware/auth_middleware.py
- [x] T014 [US1] Add verify_jwt_token dependency that extracts user_id from token in backend/src/middleware/auth_middleware.py
- [x] T015 [US1] Add get_current_user_id dependency for route handlers in backend/src/middleware/auth_middleware.py
- [x] T016 [US1] Implement UserIsolationService with get_user_owned_resources() in backend/src/services/user_isolation_service.py
- [x] T017 [US1] Add get_single_user_resource() for single resource access validation in backend/src/services/user_isolation_service.py
- [x] T018 [US1] Add check_user_owns_resource() for ownership validation in backend/src/services/user_isolation_service.py
- [x] T019 [US1] Configure middleware to return 401 "Missing authentication token" when no header in backend/src/middleware/auth_middleware.py
- [x] T020 [US1] Configure middleware to return 401 "Invalid or expired token" for bad tokens in backend/src/middleware/auth_middleware.py
- [x] T021 [US1] Ensure non-owned resource access returns 404 (not 403) in backend/src/services/user_isolation_service.py
- [x] T022 [US1] Add security logging for authentication events in backend/src/utils/logger.py
- [x] T023 [US1] Run tests T011-T012 and verify all pass

**Checkpoint**: Backend JWT verification and user isolation is complete - can verify with curl/Postman

---

## Phase 4: User Story 2 - Frontend Integrates Better Auth with JWT Plugin (Priority: P1)

**Goal**: Next.js pages use authentication with JWT management, enabling users to sign up, sign in, and have tokens automatically included in API requests

**Independent Test**: Render sign-up and sign-in forms, submit credentials, verify JWT tokens are stored and sent with subsequent API requests, verify logout clears tokens.

**User Story Reference**: User Story 2 from spec.md (P1 - Frontend Auth Flow)

### Tests for User Story 2

- [x] T024 [P] [US2] Create component tests for SignInForm in frontend/src/components/auth/__tests__/SignInForm.test.tsx
- [x] T025 [P] [US2] Create component tests for SignUpForm in frontend/src/components/auth/__tests__/SignUpForm.test.tsx
- [x] T026 [P] [US2] Create API client tests for token injection in frontend/src/lib/__tests__/api-client.test.ts

### Implementation for User Story 2

- [x] T027 [P] [US2] Implement token storage functions (saveToken, getToken, removeToken) in frontend/src/auth/auth-config.ts
- [x] T028 [P] [US2] Implement isAuthenticated() check using token expiration in frontend/src/auth/auth-config.ts
- [x] T029 [P] [US2] Implement parseJWT() for extracting claims from token in frontend/src/lib/token-utils.ts
- [x] T030 [US2] Implement SignUpForm with email/password fields and validation in frontend/src/components/auth/SignUpForm.tsx
- [x] T031 [US2] Implement SignInForm with email/password fields and validation in frontend/src/components/auth/SignInForm.tsx
- [x] T032 [US2] Implement API client with automatic Authorization header injection in frontend/src/lib/api-client.ts
- [x] T033 [US2] Add sign-up page at frontend/src/app/auth/sign-up/page.tsx
- [x] T034 [US2] Add sign-in page at frontend/src/app/auth/sign-in/page.tsx
- [x] T035 [US2] Implement logout handler that clears token and redirects in frontend/src/lib/auth-utils.ts
- [x] T036 [US2] Add expired token detection and redirect to sign-in page in frontend/src/lib/auth-utils.ts
- [x] T037 [US2] Add TypeScript interfaces for AuthResponse and JWTPayload in frontend/src/types/auth.ts
- [x] T038 [US2] Run tests T024-T026 and verify all pass

**Checkpoint**: Frontend authentication UI is complete - can test sign-up, sign-in, and API requests

---

## Phase 5: User Story 3 - System Shares JWT Secret Between Frontend and Backend (Priority: P1)

**Goal**: Both Next.js frontend and FastAPI backend use the same JWT secret from environment variables, enabling secure cross-service authentication

**Independent Test**: Set JWT_SECRET in both .env files, have frontend generate auth request, verify backend can decode tokens. Test with mismatched secrets to verify rejection.

**User Story Reference**: User Story 3 from spec.md (P1 - Cryptographic Trust Chain)

### Tests for User Story 3

- [x] T039 [P] [US3] Create cross-service token validation test in backend/tests/test_cross_service_validation.py
- [x] T040 [P] [US3] Create test for mismatched secrets rejection in backend/tests/test_cross_service_validation.py
- [x] T041 [P] [US3] Create startup validation test (missing secret fails) in backend/tests/test_auth_config.py

### Implementation for User Story 3

- [x] T042 [P] [US3] Implement BETTER_AUTH_SECRET loading in backend/src/config/settings.py
- [x] T043 [P] [US3] Add startup validation to fail if BETTER_AUTH_SECRET missing in backend/src/config/auth_config.py
- [x] T044 [US3] Ensure jwt_utils uses BETTER_AUTH_SECRET from settings in backend/src/lib/jwt_utils.py
- [x] T045 [US3] Document secret rotation behavior (invalidates existing tokens) in backend/.env.example
- [x] T046 [US3] Implement POST /auth/register endpoint with password hashing and JWT return in backend/src/api/auth.py
- [x] T047 [US3] Implement POST /auth/login endpoint with credential verification and JWT return in backend/src/api/auth.py
- [x] T048 [US3] Implement GET /auth/me protected endpoint returning current user in backend/src/api/auth.py
- [x] T049 [US3] Implement POST /auth/logout endpoint (informational for JWT) in backend/src/api/auth.py
- [x] T050 [US3] Add auth router to main FastAPI app in backend/src/main.py
- [x] T051 [US3] Run tests T039-T041 and verify all pass

**Checkpoint**: Full authentication flow works end-to-end with shared secret

---

## Phase 6: Integration Testing

**Purpose**: Verify complete authentication flow across frontend and backend

- [x] T052 Create end-to-end test: register → login → access protected resource → logout in backend/tests/integration/test_auth_flow.py
- [x] T053 [P] Test user isolation: create User A and User B, verify A cannot access B's data in backend/tests/integration/test_user_isolation_e2e.py
- [x] T054 Test expired token handling: generate old token, verify 401 response in backend/tests/integration/test_token_expiry.py
- [x] T055 Test edge cases from spec.md: token tampering, missing claims, concurrent expired requests in backend/tests/integration/test_edge_cases.py

**Checkpoint**: All integration tests pass - authentication system is production-ready

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that affect multiple user stories

- [x] T056 [P] Update quickstart.md with verified setup steps in specs/003-better-auth-jwt/quickstart.md
- [x] T057 [P] Add security headers middleware (X-Content-Type-Options, etc.) in backend/src/middleware/security.py
- [x] T058 Add CORS configuration for frontend origin in backend/src/main.py
- [x] T059 [P] Add request logging for audit trail in backend/src/utils/logger.py
- [x] T060 Code review: ensure no hardcoded secrets, all env vars documented
- [x] T061 Verify all acceptance scenarios from spec.md pass (15 total)
- [x] T062 Run full test suite and verify 100% of tests pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (Phase 3): Backend JWT verification - can start after Phase 2
  - US2 (Phase 4): Frontend auth - can start after Phase 2 (parallel with US1)
  - US3 (Phase 5): Shared secret config - depends on US1 for backend endpoints
- **Integration (Phase 6)**: Depends on all user stories being complete
- **Polish (Phase 7)**: Depends on Integration phase completion

### User Story Dependencies

- **User Story 1 (Backend JWT)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Frontend Auth)**: Can start after Foundational (Phase 2) - Independent of US1, but needs backend endpoints for testing
- **User Story 3 (Shared Secret)**: Depends on US1 (backend endpoints) for complete testing

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- US1 and US2 can be worked on in parallel after Foundational
- Tests within a story marked [P] can run in parallel
- Frontend components marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create middleware unit tests for valid/invalid/missing JWT in backend/tests/test_auth_middleware.py"
Task: "Create user isolation tests (User A cannot access User B's data) in backend/tests/test_user_isolation.py"

# Launch parallel utility implementations:
Task: "Implement UserIsolationService with get_user_owned_resources() in backend/src/services/user_isolation_service.py"
Task: "Add security logging for authentication events in backend/src/utils/logger.py"
```

## Parallel Example: User Story 2

```bash
# Launch all frontend tests together:
Task: "Create component tests for SignInForm in frontend/src/components/auth/__tests__/SignInForm.test.tsx"
Task: "Create component tests for SignUpForm in frontend/src/components/auth/__tests__/SignUpForm.test.tsx"
Task: "Create API client tests for token injection in frontend/src/lib/__tests__/api-client.test.ts"

# Launch parallel utility implementations:
Task: "Implement token storage functions (saveToken, getToken, removeToken) in frontend/src/auth/auth-config.ts"
Task: "Implement isAuthenticated() check using token expiration in frontend/src/auth/auth-config.ts"
Task: "Implement parseJWT() for extracting claims from token in frontend/src/lib/token-utils.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 3 Backend Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Backend JWT Verification)
4. Complete Phase 5: User Story 3 (Shared Secret + Auth Endpoints)
5. **STOP and VALIDATE**: Test with curl/Postman
6. Backend is functional for authentication

### Full Feature Delivery

1. Complete Setup + Foundational → Foundation ready
2. Complete User Story 1 → Backend security layer functional
3. Complete User Story 2 → Frontend auth UI functional
4. Complete User Story 3 → End-to-end auth flow works
5. Complete Integration → Verified cross-service authentication
6. Complete Polish → Production-ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Backend JWT)
   - Developer B: User Story 2 (Frontend Auth)
3. Developer C: User Story 3 (after US1 backend endpoints)
4. All: Integration testing and Polish

---

## Task Summary

| Phase | Task Count | Parallel Tasks |
|-------|------------|----------------|
| Phase 1: Setup | 5 | 3 |
| Phase 2: Foundational | 5 | 2 |
| Phase 3: US1 - Backend JWT | 13 | 2 |
| Phase 4: US2 - Frontend Auth | 15 | 6 |
| Phase 5: US3 - Shared Secret | 13 | 4 |
| Phase 6: Integration | 4 | 1 |
| Phase 7: Polish | 7 | 3 |
| **Total** | **62** | **21 parallel** |

### Tasks per User Story

- **US1 (Backend JWT Verification)**: 13 tasks
- **US2 (Frontend Auth Integration)**: 15 tasks
- **US3 (Shared Secret Configuration)**: 13 tasks

### MVP Scope (Recommended)

For minimal viable authentication:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (US1): 13 tasks
- Phase 5 (US3, backend only): 10 tasks
- **MVP Total**: ~33 tasks for backend-only authentication

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
