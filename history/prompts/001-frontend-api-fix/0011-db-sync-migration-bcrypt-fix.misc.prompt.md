---
id: 0011
title: DB sync, migration, and bcrypt fix
stage: misc
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 001-frontend-api-fix
branch: 001-frontend-api-fix
user: Lead Architect
command: db-sync-migration
labels: ["database", "migration", "bcrypt", "passlib", "neon", "e2e"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/main.py
  - backend/src/lib/jwt_utils.py
  - backend/src/models/user.py
  - backend/requirements.txt
tests:
  - POST /auth/register -> 200 (user created)
  - POST /auth/login -> 200 (token returned)
  - GET /auth/me -> 200 (user data returned)
  - GET /api/1/tasks -> 200 (empty list)
  - POST /api/1/tasks -> 201 (task created)
  - POST /auth/register (dup) -> 400 (duplicate rejected)
---

## Prompt

Verify that SQLModel models are synced with Neon DB. Run any missing migrations so that the 500 errors on register/login turn into 201/200.

## Response snapshot

Three root causes found and fixed:

1. **Missing tables**: `init_db()` (which calls `SQLModel.metadata.create_all(engine)`) was defined but never called at startup. Added `init_db()` call to `main.py` `create_app()` with model imports so both `user` and `task` tables are created on startup.

2. **passlib + bcrypt incompatibility**: `passlib==1.7.4` crashes on `bcrypt==5.0.0` (`AttributeError: module 'bcrypt' has no attribute '__about__'`). Replaced all `passlib.CryptContext` usage with direct `bcrypt` calls in `jwt_utils.py` and `user.py`. Removed `passlib` from `requirements.txt`, added `bcrypt>=4.0.0`.

3. **No migration system**: Project uses `create_all()` (CREATE TABLE IF NOT EXISTS) — no Alembic. Sufficient for current schema.

End-to-end results with live Neon DB: register 200, login 200, /auth/me 200, task list 200, task create 201, duplicate register 400.

## Outcome

- Impact: 500 errors on auth routes eliminated — register and login now return 200 with tokens
- Tests: Full E2E gate test passed (6/6 endpoints correct)
- Files: 4 files modified (main.py, jwt_utils.py, user.py, requirements.txt)
- Next prompts: Clean up test data from Neon DB, remove debug print statements before production
- Reflection: Two independent failures (missing tables + broken password hashing) combined to produce the same 500 — always check the actual error, not just the status code

## Evaluation notes (flywheel)

- Failure modes observed: passlib is unmaintained and breaks with bcrypt 4.1+; init_db() was exported but never called
- Graders run and results (PASS/FAIL): E2E gate test PASS (6/6)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add Alembic for proper schema migration management
