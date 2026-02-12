---
id: "0012"
title: Middleware v1 Prefix Route Fix
stage: misc
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 001-frontend-api-fix
branch: 001-frontend-api-fix
user: lead-architect
command: direct-prompt
labels: ["middleware", "auth", "routing", "api-prefix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/middleware/auth_middleware.py
  - backend/src/main.py
tests:
  - none
---

## Prompt

I am the Lead Architect. The middleware is STILL blocking auth routes because it incorrectly identifies them as PROTECTED.

Code Audit: Open backend/src/middleware/auth_middleware.py and check the EXEMPT_ROUTES or bypass logic.

The Mismatch: I see in the logs that the path is POST /api/v1/auth/register. If your bypass list only has /auth/register, it will fail. Update the list to include the full path or use a .endswith() check.

The 'v1' Factor: Ensure that the middleware accounts for the version prefix /api/v1/.

Fix & Verify: Update the logic so the log says -> PUBLIC route — skipping auth instead of PROTECTED route.

Show me the updated code snippet before you apply it.

## Response snapshot

Identified two-layer mismatch:
1. **Middleware** `_is_public()` checked exact paths from `PUBLIC_AUTH_PATHS` (e.g. `/auth/register`) but incoming requests had `/api/v1/auth/register` — no match, so treated as PROTECTED → 401.
2. **Route mounting** in `main.py` used `app.include_router(auth_router)` with no prefix, so even if middleware passed, FastAPI would 404 on `/api/v1/auth/register`.

Applied two fixes:
- `auth_middleware.py`: Added `_API_PREFIXES = ("/api/v1",)` and rewrote `_is_public()` to strip the version prefix before matching against `PUBLIC_AUTH_PATHS`.
- `main.py`: Changed `app.include_router(auth_router)` → `app.include_router(auth_router, prefix="/api/v1")` (same for tasks_router).

## Outcome

- ✅ Impact: Auth routes (/api/v1/auth/register, /api/v1/auth/login) now correctly identified as PUBLIC and routed to actual handlers
- 🧪 Tests: No automated tests run; manual verification needed
- 📁 Files: 2 files modified (auth_middleware.py, main.py)
- 🔁 Next prompts: Restart backend server, test POST /api/v1/auth/register, verify logs show PUBLIC route
- 🧠 Reflection: The mismatch was a two-layer problem — middleware bypass AND route prefix — fixing only one layer would have left the other broken

## Evaluation notes (flywheel)

- Failure modes observed: Frontend .env.local set NEXT_PUBLIC_API_URL to include /api/v1 but backend had no version prefix on routes
- Graders run and results (PASS/FAIL): N/A — manual review
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Restart backend and test registration flow end-to-end
