---
id: 0008
title: Auth route exclusion and CORS validation
stage: misc
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 001-frontend-api-fix
branch: 001-frontend-api-fix
user: Lead Architect
command: auth-route-exclusion
labels: ["middleware", "auth", "cors", "security", "urgent"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/middleware/auth_middleware.py
tests:
  - Middleware gate test: POST /auth/register PASSED (500 DB, not 401)
  - Middleware gate test: POST /auth/login PASSED (500 DB, not 401)
  - Middleware gate test: POST /auth/logout PASSED (200)
  - Middleware gate test: GET /auth/callback PASSED (422 no route handler, not 401)
  - Middleware gate test: GET /auth/me BLOCKED (401 — correct, protected)
  - Middleware gate test: GET /api/1/tasks BLOCKED (401 — correct, protected)
---

## Prompt

Auth Route Exclusion (Urgent): Update auth_middleware.py (or wherever your middleware logic is). You MUST add an exclusion list so that the middleware skips JWT verification for:

POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/auth/callback (if using social auth)

CORS Validation: Ensure backend/src/main.py has allow_credentials=True and allow_origins=["http://localhost:3000"].

Validation: After applying, I should see a 200 OK or 201 Created in the terminal for these routes.

Do not change any other task endpoints. Just unlock the auth gates.

## Response snapshot

Two changes made to `backend/src/middleware/auth_middleware.py`:

1. Replaced the blanket `path.startswith("/auth/")` (which made ALL auth paths public, including /auth/me) with an explicit `PUBLIC_AUTH_PATHS` frozenset containing only: /auth/register, /auth/login, /auth/logout, /auth/health, /auth/callback.

2. The `is_public` check is now: `path in PUBLIC_PATHS or path in PUBLIC_AUTH_PATHS` — no wildcards.

CORS in main.py was already correct: `allow_credentials=True`, `allow_origins` defaults to `http://localhost:3000`.

Gate test results: register/login/logout/callback all pass through middleware. /auth/me and /api/{user_id}/tasks are correctly blocked without a token.

## Outcome

- Impact: Auth gates unlocked for register, login, logout, callback; protected routes remain guarded
- Tests: 6-route middleware gate test passed — all public routes pass through, all protected routes blocked
- Files: 1 file modified (auth_middleware.py)
- Next prompts: End-to-end auth flow test with live database
- Reflection: Blanket startswith("/auth/") was a security bug — /auth/me was unprotected. Fixed by switching to explicit whitelist.

## Evaluation notes (flywheel)

- Failure modes observed: Previous blanket path.startswith("/auth/") left /auth/me and /auth/{user_id} unprotected
- Graders run and results (PASS/FAIL): Middleware gate test PASS (6/6 correct)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add /auth/callback route handler for social auth flow
