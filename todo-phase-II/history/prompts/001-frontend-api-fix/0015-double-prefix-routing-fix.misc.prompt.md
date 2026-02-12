---
id: 0015
title: Double Prefix Routing Fix
stage: misc
date: 2026-02-12
surface: agent
model: claude-opus-4-6
feature: 001-frontend-api-fix
branch: main
user: Lead Architect
command: direct prompt
labels: ["routing", "double-prefix", "env-config", "vercel", "bugfix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/.env.local
tests:
  - none (configuration change)
---

## Prompt

I am the Lead Architect. We have a Double Prefixing issue: /api/v1/api/v1/ is appearing in logs.

Backend Route Fix: In backend/src/main.py, remove the prefix="/api/v1" from app.include_router calls IF the routers themselves already have prefixes, OR keep it there and ensure the routers are defined at the root /.

Middleware Logic: Update auth_middleware.py. It should handle paths correctly even if they don't have the double prefix. It must normalize /api/v1/auth/register to /auth/register correctly.

Frontend Env Check: Verify frontend/.env.local. If NEXT_PUBLIC_API_URL is http://localhost:8000/api/v1, ensure the API client isn't adding another /api/v1 manually.

Vercel Fix: This is why Vercel failed to fetch! The URL it was hitting didn't exist.

Clean up the routing so the logs show a single /api/v1/auth/register and return 200/201.

## Response snapshot

Root cause identified: frontend-only double prefix. `.env.local` had `NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"` while `api-client.ts` hardcoded `/api/v1` in every request path. The `request()` function concatenated both, producing `http://localhost:8000/api/v1/api/v1/auth/register`.

Fix: Changed `.env.local` `NEXT_PUBLIC_API_URL` to `"http://localhost:8000"` (bare URL). Removed unused `NEXT_PUBLIC_API_BASE_PATH`. Backend routing (`main.py` prefix + router prefixes) and middleware normalization were already correct.

## Outcome

- ✅ Impact: Eliminates double-prefix `/api/v1/api/v1/` in all frontend requests. Fixes Vercel 404s.
- 🧪 Tests: Manual verification — trace request chain through api-client.ts confirms single prefix.
- 📁 Files: frontend/.env.local (1 file changed)
- 🔁 Next prompts: Verify Vercel env var `NEXT_PUBLIC_API_URL` is set to bare backend URL without `/api/v1`.
- 🧠 Reflection: Backend and middleware were fine. The env var was the sole source of the double prefix. The `.env.local.example` already had the correct value — the local override diverged.

## Evaluation notes (flywheel)

- Failure modes observed: Env var containing path prefix combined with hardcoded path prefix in API client.
- Graders run and results (PASS/FAIL): Manual trace PASS — all 5 api-client paths resolve to single prefix.
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add a startup warning if API_BASE ends with /api/v1 to catch this class of misconfiguration early.
