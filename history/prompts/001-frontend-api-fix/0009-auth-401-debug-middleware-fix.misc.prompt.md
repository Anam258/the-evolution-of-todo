---
id: 0009
title: Auth 401 debug — middleware print and early return
stage: misc
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 001-frontend-api-fix
branch: 001-frontend-api-fix
user: Lead Architect
command: auth-401-debug
labels: ["middleware", "auth", "debug", "cors", "401"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/middleware/auth_middleware.py
  - backend/src/main.py
tests:
  - Gate test: POST /auth/register PASSED (500 DB, not 401)
  - Gate test: POST /auth/login PASSED (500 DB, not 401)
  - Gate test: POST /auth/logout PASSED (200)
  - Gate test: GET /auth/callback PASSED (422 no handler, not 401)
  - Gate test: POST /api/v1/auth/register PASSED (404 no route, not 401)
  - Gate test: POST /api/v1/auth/login PASSED (404 no route, not 401)
  - Gate test: GET /auth/me BLOCKED (401 — correct)
  - Gate test: GET /api/1/tasks BLOCKED (401 — correct)
  - Gate test: GET / PASSED (200)
  - Gate test: GET /health PASSED (200)
---

## Prompt

Phase II is blocked by a persistent 401 on Auth routes. Do exactly this:

Print Debugging: Add a print(f'Checking path: {request.url.path}') statement at the very start of your middleware's dispatch method.

Exact Match: Ensure the exclusion logic uses a prefix check or includes the exact string /api/v1/auth/register and /api/v1/auth/login.

CORS Order: In main.py, move CORSMiddleware so it is added AFTER auth_middleware (FastAPI executes them in reverse order, so CORS needs to be 'outside').

Response Check: If the path is an auth route, the middleware must return await call_next(request) immediately without even looking for a header.

Show me the logs after you add the print statements so we can see what the middleware is 'thinking'.

## Response snapshot

Four changes applied:

1. **Print debugging**: Every request now logs `[AUTH-MW] Checking path: METHOD /path (normalized: /path)` plus the decision (`PUBLIC route, skipping JWT check` / `PROTECTED route, NO valid token — returning 401` / `PROTECTED route, user_id=N — OK`).

2. **Exact match for /api/v1/auth/***: PUBLIC_AUTH_PATHS now includes both `/auth/register` and `/api/v1/auth/register` (and login, logout, health, callback) so the middleware covers both URL conventions.

3. **CORS order**: main.py middleware registration documented with explicit execution-order comment. Registration: SecurityHeaders → JWTAuth → CORS. Execution (reversed): CORS → JWTAuth → SecurityHeaders → route.

4. **Early return on public routes**: Public paths now `return await call_next(request)` immediately after setting state to None — no header inspection, no token parsing.

Bug fix: `rstrip("/")` on `"/"` was producing `""`, which didn't match `"/"` in PUBLIC_PATHS. Fixed with `raw.rstrip("/") or "/"`.

## Outcome

- Impact: Auth routes confirmed unblocked; debug logs show middleware decision-making
- Tests: 10-route gate test — 6 public PASSED, 2 protected BLOCKED, 2 infra PASSED (10/10 correct)
- Files: 2 files modified (auth_middleware.py, main.py)
- Next prompts: Test with live Neon DB to confirm register/login return 200/201
- Reflection: The root "/" normalization bug was subtle — would have blocked the API root endpoint in production

## Evaluation notes (flywheel)

- Failure modes observed: rstrip("/") on "/" produces "" — path normalization must preserve root
- Graders run and results (PASS/FAIL): 10-route gate test PASS (10/10)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Remove print debug statements before production deploy
