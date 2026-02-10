---
id: PHR-005
title: Auth System JWT Integration Spec
stage: spec
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-better-auth-jwt
branch: 003-better-auth-jwt
user: claude
command: /sp.specify "Authentication System and JWT Integration using Better Auth and FastAPI"
labels: [auth,jwt,better-auth,fastapi,specification]
links:
  spec: ../specs/003-better-auth-jwt/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-better-auth-jwt/spec.md
 - specs/003-better-auth-jwt/checklists/requirements.md
tests:
 - specs/003-better-auth-jwt/checklists/requirements.md
---

## Prompt

Authentication System and JWT Integration using Better Auth and FastAPI

Target audience: Full-stack developers and Security Engineers
Focus: Implementing a secure, cross-service authentication flow using Shared Secret JWTs.

Success criteria:
- Better Auth is configured in the Frontend to issue JWT tokens.
- A shared `BETTER_AUTH_SECRET` is established between Next.js and FastAPI.
- FastAPI middleware is created to intercept every request, verify the JWT, and extract `user_id`.
- User isolation is enforced: All database queries automatically filter results by the authenticated `user_id`.
- Protected routes return `401 Unauthorized` if a valid token is missing.

Constraints:
- Auth Library: Better Auth (with JWT plugin).
- Backend: FastAPI (Python) with JWT verification logic.
- Security: Must use Bearer Token in the Authorization header.
- Implementation: Code must be generated based on this spec only.

Not building:
- Database schema or tables (Already covered in Spec 1).
- Main Todo CRUD logic

## Response snapshot

Specification created for Authentication System and JWT Integration using Better Auth and FastAPI. The spec includes comprehensive user stories for backend JWT verification with user isolation, frontend Better Auth integration, and shared JWT secret configuration. Functional requirements cover authentication core, token management, configuration, and user isolation. Success criteria define complete authentication flow, backend security layer, user data isolation, shared secret configuration, token lifecycle management, error handling, and documentation requirements. The specification addresses assumptions, out-of-scope items, and edge cases to ensure a robust authentication system.

## Outcome

- ✅ Impact: Created comprehensive authentication specification with JWT integration between Better Auth and FastAPI
- 🧪 Tests: Created specification quality checklist to validate requirements
- 📁 Files: Generated spec.md and requirements checklist in feature directory
- 🔁 Next prompts: Ready for planning phase with /sp.plan
- 🧠 Reflection: Specification addresses all requirements with proper security considerations for user isolation

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase