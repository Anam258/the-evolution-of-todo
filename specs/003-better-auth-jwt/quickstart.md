# Quickstart Guide: Authentication System and JWT Integration

**Feature**: 003-better-auth-jwt
**Date**: 2026-01-16

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Neon PostgreSQL account (from 001-db-schema)
- Git

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
cd todo-phase-II
```

### 2. Configure Environment Variables

**Backend** (`backend/.env`):
```env
# Database (from Neon console)
DATABASE_URL="postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require"

# Authentication (CRITICAL: Same secret in both services)
BETTER_AUTH_SECRET="your-32-character-secret-key-here-must-be-at-least-32-chars"

# JWT Configuration (optional, defaults shown)
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_DELTA="1440"  # 24 hours in minutes

# CORS Configuration
ALLOWED_ORIGINS="http://localhost:3000"

# Server Configuration
PORT="8000"
```

**Frontend** (`frontend/.env.local`):
```env
# API Configuration
NEXT_PUBLIC_API_URL="http://localhost:8000"

# Auth URLs (for Better Auth client)
NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:3000"
NEXT_PUBLIC_BETTER_AUTH_BASE_PATH="/api/auth"
```

> **CRITICAL**: The `BETTER_AUTH_SECRET` must be:
> - At least 32 characters long
> - Identical in backend and frontend environments
> - Never committed to version control
> - Different per environment (dev/staging/prod)

Generate a secure secret:
```bash
# Using OpenSSL
openssl rand -base64 32

# Or using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

Required packages (already in requirements.txt):
- `fastapi>=0.100.0`
- `uvicorn>=0.23.0`
- `sqlmodel>=0.0.14`
- `python-jose[cryptography]>=3.3.0`
- `passlib[bcrypt]>=1.7.4`
- `python-multipart>=0.0.6`
- `psycopg2-binary>=2.9.0`
- `python-dotenv>=1.0.0`
- `psutil>=5.9.0`

**Frontend:**
```bash
cd frontend
npm install
```

### 4. Start the Application

**Backend** (Terminal 1):
```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"todo-api"}
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```

Frontend should be available at: http://localhost:3000

---

## Architecture Overview

### Backend Components

```
backend/src/
├── main.py                      # FastAPI application factory
├── api/
│   └── auth.py                  # Authentication endpoints
├── middleware/
│   ├── auth_middleware.py       # JWT verification middleware
│   └── security.py              # Security headers middleware
├── lib/
│   └── jwt_utils.py             # JWT creation/verification utilities
├── services/
│   ├── auth_service.py          # Authentication business logic
│   └── user_isolation_example.py # User isolation patterns
├── models/
│   └── user.py                  # User SQLModel definitions
├── config/
│   ├── settings.py              # Environment configuration
│   └── auth_config.py           # Auth-specific configuration
└── database/
    └── connection.py            # Database connection setup
```

### Frontend Components

```
frontend/src/
├── app/
│   └── auth/
│       ├── sign-in/page.tsx     # Sign-in page
│       └── sign-up/page.tsx     # Sign-up page
├── components/
│   └── auth/
│       ├── SignInForm.tsx       # Sign-in form component
│       └── SignUpForm.tsx       # Sign-up form component
├── lib/
│   ├── api-client.ts            # API client with auto-token injection
│   ├── auth-utils.ts            # Authentication utilities
│   └── token-utils.ts           # Token management utilities
└── auth/
    └── auth-config.ts           # Auth configuration and token storage
```

---

## API Usage Examples

### Register a New User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123"
  }'
```

**Success Response** (200):
```json
{
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Response** (400 - User exists):
```json
{
  "detail": "User with this email already exists"
}
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123"
  }'
```

**Success Response** (200):
```json
{
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Response** (401 - Invalid credentials):
```json
{
  "detail": "Incorrect email or password"
}
```

### Get Current User (Protected)

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Success Response** (200):
```json
{
  "data": {
    "user_id": 1,
    "email": "user@example.com"
  }
}
```

**Error Response** (401 - Missing token):
```json
{
  "detail": "Missing authentication token"
}
```

**Error Response** (401 - Invalid/expired token):
```json
{
  "detail": "Invalid or expired token"
}
```

### Logout

```bash
curl -X POST http://localhost:8000/auth/logout
```

**Response** (200):
```json
{
  "message": "Successfully logged out"
}
```

> **Note**: For JWT-based auth, logout is client-side only. The server endpoint is informational.

---

## Frontend Usage

### Sign-In Form Integration

```tsx
// Using the provided SignInForm component
import SignInForm from '@/components/auth/SignInForm';

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <SignInForm
        redirectAfterSignIn="/dashboard"
        onSignIn={(userData) => {
          console.log('Logged in:', userData.email);
        }}
      />
    </div>
  );
}
```

### API Client Usage

```typescript
import { apiClient } from '@/lib/api-client';

// Token is automatically included from localStorage
const response = await apiClient.get('/todos');
const todos = response.data;

// Create a new todo (token auto-included)
const newTodo = await apiClient.post('/todos', {
  title: 'New todo',
  description: 'Description here'
});
```

### Check Authentication Status

```typescript
import { isAuthenticated, getToken } from '@/auth/auth-config';

if (isAuthenticated()) {
  const token = getToken();
  // User is logged in
} else {
  // Redirect to sign-in
  window.location.href = '/auth/sign-in';
}
```

### Logout

```typescript
import { removeToken } from '@/auth/auth-config';

function handleLogout() {
  removeToken();
  window.location.href = '/auth/sign-in';
}
```

---

## Testing the Authentication Flow

### 1. Test Registration

```bash
# Register a new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

### 2. Test Login

```bash
# Login and capture token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}' \
  | jq -r '.data.token')

echo "Token: $TOKEN"
```

### 3. Test Protected Endpoint

```bash
# Access /auth/me with token
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Test Invalid Token

```bash
# Should return 401
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer invalid-token-here"
```

### 5. Test Missing Token

```bash
# Should return 401
curl -X GET http://localhost:8000/auth/me
```

---

## Troubleshooting

### Backend Won't Start

**Error**: `ValueError: BETTER_AUTH_SECRET environment variable not set`

**Solution**: Create `backend/.env` file with `BETTER_AUTH_SECRET` value.

### Token Verification Fails

**Error**: `401 Invalid or expired token`

**Possible causes**:
1. Different `BETTER_AUTH_SECRET` between services
2. Token has expired (24-hour default)
3. Malformed token string

**Solution**: Ensure secrets match and generate a new token via login.

### CORS Errors

**Error**: `Access-Control-Allow-Origin` header missing

**Solution**: Verify `ALLOWED_ORIGINS` in backend `.env` includes your frontend URL.

### Database Connection Failed

**Error**: `Connection refused` or `SSL required`

**Solution**:
1. Check `DATABASE_URL` format
2. Ensure `?sslmode=require` is in the URL for Neon
3. Verify Neon project is active

---

## Security Checklist

- [ ] `BETTER_AUTH_SECRET` is at least 32 characters
- [ ] Secrets are never committed to Git
- [ ] Different secrets for dev/staging/prod
- [ ] HTTPS enabled in production
- [ ] CORS whitelist is restrictive in production
- [ ] Rate limiting is enabled on auth endpoints

---

## Next Steps

After completing this setup:

1. Run the test suite: `cd backend && pytest`
2. Verify frontend auth flow: http://localhost:3000/auth/sign-in
3. Implement protected Todo endpoints with user isolation
4. Add integration tests for user isolation

See `tasks.md` for the complete implementation task list.
