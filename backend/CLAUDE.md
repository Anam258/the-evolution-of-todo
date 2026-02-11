# Backend — TaskPulse AI

## Tech Stack

- Python 3.11+
- FastAPI
- SQLModel (SQLAlchemy 2.0 under the hood)
- Neon Serverless PostgreSQL
- python-jose (JWT) + passlib (bcrypt hashing)

## Project Structure

```
backend/src/
  main.py            # App factory (create_app), middleware stack, root routes
  database/          # Engine, session, init_db (CREATE TABLE IF NOT EXISTS)
  models/
    user.py          # User SQLModel with password hashing
    task.py          # Task SQLModel with user isolation
  api/
    auth.py          # /api/v1/auth/* routes (register, login, me, health)
    tasks.py         # /api/v1/{user_id}/tasks/* routes (CRUD)
  middleware/
    auth_middleware.py  # JWTAuthMiddleware — validates Bearer tokens
    security.py        # SecurityHeadersMiddleware — CSP, HSTS, etc.
  config/
    auth_config.py   # AuthConfig (SECRET_KEY, algorithm, expiry)
  services/          # Business logic services
  utils/             # Port checker, helpers
  lib/               # Shared library code
```

## Auth System

- JWT tokens signed with HS256 via python-jose
- Passwords hashed with passlib bcrypt
- `JWTAuthMiddleware` intercepts all requests except public paths
- Public paths: `/`, `/health`, `/docs`, `/openapi.json`, `/api/v1/auth/*`

## Route Structure

- `/api/v1/auth/register` — POST, create account + return JWT
- `/api/v1/auth/login` — POST, authenticate + return JWT
- `/api/v1/auth/me` — GET, current user profile (protected)
- `/api/v1/auth/health` — GET, auth service health
- `/api/v1/{user_id}/tasks/` — GET/POST (protected)
- `/api/v1/{user_id}/tasks/{task_id}` — GET/PUT/PATCH/DELETE (protected)

## Middleware Stack

Execution order (FastAPI reverses registration order):

```
CORS → JWTAuth → SecurityHeaders → route handler
```

## User Isolation

All database queries for tasks are scoped by `user_id` extracted from the JWT token. Accessing another user's resources returns 404 (not 403) to prevent enumeration.

## Configuration

Environment variables via `.env`:

- `DATABASE_URL` — Neon PostgreSQL connection string
- `SECRET_KEY` — JWT signing secret (min 32 chars)
- `ALLOWED_ORIGINS` — Comma-separated CORS origins

## Code Standards

- Type hints on all function signatures
- SQLModel for both Pydantic validation and ORM mapping
- Separate Create/Read/Update schemas per model
- Startup validation: config checked before app accepts requests
