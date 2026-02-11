---
id: 0007
title: Gap analysis — backend route & middleware fix
stage: misc
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 001-frontend-api-fix
branch: 001-frontend-api-fix
user: Lead Architect
command: gap-analysis-fix
labels: ["gap-analysis", "api-contract", "middleware", "user-isolation", "security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/api/tasks.py
  - backend/src/middleware/auth_middleware.py
  - backend/src/main.py
tests:
  - Python import verification for tasks.py, auth_middleware.py, main.py
---

## Prompt

Address the gaps found in the audit report:

Update all backend routes in /backend/src/api/tasks.py to match the required pattern: /api/{user_id}/tasks.

Register the auth_middleware in backend/src/main.py using app.add_middleware() to ensure it's a true ASGI middleware.

Ensure the backend validates that the {user_id} in the URL matches the user_id extracted from the JWT token.

## Response snapshot

Three gaps from the Phase II audit were remediated across three backend files:

1. **API Contract (tasks.py)**: All 6 endpoints migrated from `/api/tasks` to `/api/{user_id}/tasks[/{task_id}]`. A shared `_enforce_ownership()` helper rejects requests where URL user_id != JWT user_id with HTTP 403.

2. **Middleware Registration (main.py)**: `JWTAuthMiddleware` (class-based, extending `BaseHTTPMiddleware`) registered via `app.add_middleware(JWTAuthMiddleware)` — executes before every request, extracts JWT claims into `request.state`, and rejects unauthenticated requests to protected paths with 401.

3. **User ID Validation (defence-in-depth)**: Every route handler calls `_enforce_ownership(url_user_id, jwt_user_id)` ensuring the path parameter matches the token claim. The middleware provides the first layer (authn), the route provides the second (authz).

Frontend `api-client.ts` was already aligned — all task calls use `/api/${uid}/tasks` pattern with `requireUserId()` extracting the user_id from the stored JWT.

Import verification passed for all three backend modules.

## Outcome

- Impact: All 3 audit gaps (API contract, middleware registration, URL/JWT validation) closed
- Tests: Python import verification passed for all 3 modified modules; route listing confirmed 6 endpoints on /api/{user_id}/tasks pattern
- Files: 3 files modified (tasks.py, auth_middleware.py, main.py)
- Next prompts: Frontend integration testing, end-to-end auth flow verification
- Reflection: Defence-in-depth pattern (middleware authn + route-level authz) is the correct approach for user isolation

## Evaluation notes (flywheel)

- Failure modes observed: Initial function-based middleware caused call_next issues; resolved by switching to class-based BaseHTTPMiddleware
- Graders run and results (PASS/FAIL): Import verification PASS, route listing PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add integration tests for 403 on cross-user URL access
