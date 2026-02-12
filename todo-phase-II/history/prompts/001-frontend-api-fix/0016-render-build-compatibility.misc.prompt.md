---
id: 0016
title: Render Build Compatibility
stage: misc
date: 2026-02-12
surface: agent
model: claude-opus-4-6
feature: 001-frontend-api-fix
branch: main
user: Lead Architect
command: direct prompt
labels: ["render", "deployment", "dependencies", "cors", "python-runtime"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/requirements.txt
  - backend/runtime.txt
  - backend/src/main.py
tests:
  - none (deployment configuration)
---

## Prompt

I am the Lead Architect. We need the backend LIVE on Render immediately to finalize Phase II.

Fix Dependencies: In backend/requirements.txt, update these specific lines:
- Change bcrypt to bcrypt==4.0.1
- Change passlib to passlib==1.7.4 (This prevents the metadata generation error on Python 3.13).

Set Runtime: Create a file backend/runtime.txt and add the text python-3.11.10 to ensure Render uses a stable Python version.

Sync CORS: Ensure backend/src/main.py includes your Render URL and Vercel URL in allow_origins.

Commit these changes as 'fix: render build compatibility' and push to main.

## Response snapshot

Applied all requested changes:
1. Pinned bcrypt==4.0.1, added passlib==1.7.4 in requirements.txt
2. Created backend/runtime.txt with python-3.11.10
3. Added https://*.onrender.com to default CORS origins in main.py
4. Also added missing psutil and psycopg2-binary dependencies that would crash on Render

Committed as 91abb36 and pushed to origin/main.

## Outcome

- ✅ Impact: Backend should now build and run on Render with correct Python version and all dependencies.
- 🧪 Tests: None — deployment config change; verified by Render build.
- 📁 Files: 3 files changed (requirements.txt, runtime.txt, main.py)
- 🔁 Next prompts: Monitor Render build logs; set ALLOWED_ORIGINS, DATABASE_URL, SECRET_KEY env vars in Render dashboard.
- 🧠 Reflection: Two hidden missing deps (psutil, psycopg2-binary) would have caused ImportError on Render even after the requested fixes.

## Evaluation notes (flywheel)

- Failure modes observed: Missing runtime dependencies not caught locally because they were pre-installed in dev environment.
- Graders run and results (PASS/FAIL): N/A — awaiting Render build.
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add a CI step that installs from requirements.txt in a clean venv to catch missing deps.
