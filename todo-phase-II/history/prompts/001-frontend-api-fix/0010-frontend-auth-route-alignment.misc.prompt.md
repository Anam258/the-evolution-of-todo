---
id: 0010
title: Frontend auth route alignment audit
stage: misc
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 001-frontend-api-fix
branch: 001-frontend-api-fix
user: Lead Architect
command: frontend-auth-route-alignment
labels: ["frontend", "auth", "api-contract", "cleanup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/middleware/auth_middleware.py
tests:
  - Gate test: 8/8 routes OK (register/login PASS, me/tasks BLOCK, root/health PASS)
---

## Prompt

Lead Architect check: The gate tests show a 404 for /api/v1/auth/register because the backend routes are at /auth/register. Update the frontend api.ts or auth config to match the backend's auth route prefix exactly so we get a 200/201 instead of a 404.

## Response snapshot

Audit of every frontend auth call site found all paths already correctly use `/auth/*` — matching the backend exactly:

- `api-client.ts:108` → `'/auth/register'`
- `api-client.ts:113` → `'/auth/login'`
- `api-client.ts:117` → `'/auth/me'`
- `SignInForm.tsx:51` → `${NEXT_PUBLIC_API_URL}/auth/login`
- `SignUpForm.tsx:68` → `${NEXT_PUBLIC_API_URL}/auth/register`
- `sign-in/page.tsx:24` → `authApi.login()` → `/auth/login`
- `sign-up/page.tsx:35` → `authApi.register()` → `/auth/register`

The 404 in the previous gate test came from `/api/v1/auth/*` entries that were added to the middleware exclusion list but pointed to no actual backend route. Those dead-weight entries have been removed from `PUBLIC_AUTH_PATHS`.

No frontend changes needed — the contract is already aligned.

## Outcome

- Impact: Removed misleading /api/v1/auth/* entries from middleware; confirmed frontend already aligned
- Tests: 8/8 gate test passed
- Files: 1 file modified (auth_middleware.py — cleanup only)
- Next prompts: Test with live Neon DB to get 200/201 on register/login
- Reflection: The 404 was a test artifact, not a real mismatch — always audit the actual call sites before changing paths

## Evaluation notes (flywheel)

- Failure modes observed: Adding phantom paths to exclusion lists creates false confidence
- Graders run and results (PASS/FAIL): 8/8 gate test PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Connect live Neon DB and verify register returns 201
