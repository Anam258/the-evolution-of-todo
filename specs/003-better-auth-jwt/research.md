# Research: Authentication System and JWT Integration

**Feature**: 003-better-auth-jwt
**Date**: 2026-01-16
**Status**: Complete

## Executive Summary

This research document resolves all technical unknowns for implementing JWT authentication with Better Auth integration. The existing codebase already has significant foundation including FastAPI middleware, JWT utilities, and frontend auth components. The focus is on completing integration and ensuring cross-service token verification.

---

## Research Area 1: Better Auth JWT Plugin Integration

### Question
How does Better Auth handle JWT tokens and what plugin configuration is required for cross-service verification?

### Research Findings

**Better Auth Architecture**:
- Better Auth is a TypeScript-first authentication library designed for Next.js/React applications
- It supports multiple authentication strategies including email/password, OAuth, and custom providers
- JWT tokens are used for stateless session management with configurable secrets

**Current Implementation Status**:
The frontend already has custom JWT handling in `frontend/src/auth/auth-config.ts` that:
- Stores tokens in localStorage
- Validates token expiration client-side
- Provides Authorization header construction

**Decision**: Continue with custom JWT implementation
**Rationale**:
- Better Auth's default session handling uses database sessions, not pure JWT
- The existing implementation already follows JWT best practices
- Custom implementation provides explicit control over token claims (user_id, email, iat, exp)

**Alternatives Considered**:
1. **Pure Better Auth sessions** - Rejected: Requires server-side session storage, not pure stateless JWT
2. **Better Auth with jwt plugin** - Partially applicable: Plugin exists but our custom implementation is more transparent
3. **Custom JWT implementation (chosen)** - Current approach with python-jose backend, manual frontend handling

---

## Research Area 2: JWT Secret Sharing Strategy

### Question
How should the JWT_SECRET be shared between Next.js frontend and FastAPI backend?

### Research Findings

**Environment Variable Approach** (Selected):
```
# Backend (.env)
BETTER_AUTH_SECRET=your-32-character-secret-key-here

# Frontend (.env.local)
BETTER_AUTH_SECRET=your-32-character-secret-key-here
```

**Current Implementation**:
- Backend reads from `BETTER_AUTH_SECRET` in `backend/src/lib/jwt_utils.py:11`
- Frontend auth config doesn't directly sign tokens (backend does)

**Security Considerations**:
1. Secret must be minimum 32 characters
2. Never commit secrets to version control
3. Use different secrets per environment (dev/staging/prod)
4. Backend startup validation exists in `auth_config.py`

**Decision**: Use single shared `BETTER_AUTH_SECRET` environment variable
**Rationale**:
- Simple and effective for MVP
- Backend generates and validates all tokens
- Frontend only stores/sends tokens, never signs them
- Aligns with constitution requirement (Principle V)

**Alternatives Considered**:
1. **Asymmetric keys (RS256)** - Rejected for MVP: Adds complexity without clear benefit for single-tenant app
2. **Multiple secrets with rotation** - Out of scope per spec
3. **Single shared secret (chosen)** - Simple, effective, secure when combined with HTTPS

---

## Research Area 3: FastAPI JWT Middleware Best Practices

### Question
What is the best pattern for JWT validation middleware in FastAPI?

### Research Findings

**Current Implementation Analysis** (`backend/src/middleware/auth_middleware.py`):
- Uses FastAPI's `HTTPBearer` security scheme
- `verify_jwt_token()` dependency for protected routes
- `get_current_user_id()` extracts user_id from token
- Returns 401 with specific error messages

**Best Practices Implemented**:
1. ✅ Fail-closed security (invalid token = 401)
2. ✅ Token expiration validation
3. ✅ user_id extraction from `sub` or `user_id` claim
4. ✅ WWW-Authenticate header on 401 responses

**Decision**: Current implementation is sound, minor enhancements needed
**Rationale**:
- Follows OAuth 2.0 Bearer Token specification
- Clear error messages without exposing internals
- Dependency injection pattern enables clean route protection

**Enhancements Identified**:
1. Add algorithm validation (ensure only HS256 accepted) - Already in jwt_utils.py
2. Ensure consistent error messages across all failure modes
3. Add logging for security-relevant events (already exists in logger.py)

---

## Research Area 4: User Isolation Implementation

### Question
How should database queries be automatically scoped to the authenticated user?

### Research Findings

**Current Implementation** (`backend/src/services/user_isolation_example.py`):
- `UserIsolationService` class with generic query scoping
- `get_user_owned_resources()` - filters by user_id
- `get_single_user_resource()` - validates ownership before returning
- `check_user_owns_resource()` - returns boolean for ownership

**Pattern Analysis**:
The service uses a reusable pattern where:
1. All queries include `WHERE user_id = ?` clause
2. Single resource access validates ownership before returning data
3. Non-owned resources return `None` (mapped to 404 in API layer)

**Decision**: Use established UserIsolationService pattern
**Rationale**:
- Pattern already proven in codebase
- Prevents accidental queries without user scoping
- Centralized enforcement is easier to audit

**Implementation in Todo Feature**:
```python
# All todo queries will use:
todos = user_isolation_service.get_user_owned_resources(db, Todo, user_id)

# Single todo access:
todo = user_isolation_service.get_single_user_resource(db, Todo, todo_id, user_id)
# Returns None if not owned -> API returns 404
```

---

## Research Area 5: Token Claims Structure

### Question
What claims should be included in JWT tokens for this application?

### Research Findings

**Required Claims (per spec FR-005)**:
| Claim | Type | Purpose |
|-------|------|---------|
| `sub` | string (user_id) | Subject - primary user identifier |
| `user_id` | int | Explicit user ID for backward compatibility |
| `email` | string | User's email address |
| `iat` | int (timestamp) | Issued at time |
| `exp` | int (timestamp) | Expiration time |

**Current Implementation** (`jwt_utils.py:43-62`):
```python
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Decision**: Include both `sub` and `user_id` claims
**Rationale**:
- `sub` follows JWT standard (RFC 7519)
- `user_id` provides explicit integer identifier
- Both supported in `get_user_id_from_token()` (lines 127-149)

**Token Lifetime**:
- Default: 24 hours (1440 minutes)
- Configurable via `JWT_EXPIRATION_DELTA` env var
- No refresh tokens in MVP (per spec assumption)

---

## Research Area 6: Frontend Token Storage

### Question
What is the most secure way to store JWT tokens in the browser?

### Research Findings

**Current Implementation** (`auth-config.ts`):
- Tokens stored in `localStorage`
- Retrieved via `getToken()` function
- Cleared on logout via `removeToken()`

**Security Trade-offs**:

| Method | XSS Vulnerable | CSRF Vulnerable | Persistence |
|--------|---------------|-----------------|-------------|
| localStorage | Yes | No | Persists |
| sessionStorage | Yes | No | Tab only |
| HttpOnly Cookie | No | Yes | Configurable |
| Memory | Yes | No | None |

**Decision**: Continue with localStorage for MVP
**Rationale**:
1. Simple implementation
2. XSS is mitigated by React's default escaping
3. Constitution allows this approach
4. Cookie-based would require backend changes and CSRF handling

**Future Enhancement** (out of scope):
- HttpOnly cookie with SameSite=Strict for production
- Refresh token rotation for extended sessions

---

## Research Area 7: Error Response Standardization

### Question
How should authentication errors be returned to clients?

### Research Findings

**Current API Response Structure** (from constitution):
```json
{
  "data": { ... },
  "error": { "code": "...", "message": "..." }
}
```

**Authentication Error Codes** (per spec SC-006):
| Scenario | HTTP Status | Error Message |
|----------|-------------|---------------|
| Missing Authorization header | 401 | "Missing authentication token" |
| Invalid token signature | 401 | "Invalid or expired token" |
| Expired token | 401 | "Invalid or expired token" |
| Missing JWT_SECRET | 500 (startup) | "BETTER_AUTH_SECRET environment variable not set" |
| User deleted but token valid | 404 | "User not found" |
| Access other user's resource | 404 | Resource not found (prevents enumeration) |

**Decision**: Use consistent error messages already implemented
**Rationale**:
- Current implementation in `auth_middleware.py` matches spec requirements
- 404 for non-owned resources prevents enumeration attacks
- Generic "Invalid or expired token" doesn't leak information about failure reason

---

## Technology Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| JWT Library (Backend) | python-jose | Already integrated, well-maintained, supports HS256 |
| JWT Library (Frontend) | Native atob/parsing | Tokens only need validation, not signing |
| Password Hashing | bcrypt via passlib | Industry standard, already implemented |
| Token Storage | localStorage | Simple, XSS mitigated by React |
| Secret Sharing | Environment variable | Simple, secure, different per environment |
| Session Management | Stateless JWT | No server-side session storage needed |
| User Isolation | Query-level WHERE clause | Centralized via UserIsolationService |
| Algorithm | HS256 | Symmetric signing, sufficient for shared secret approach |
| 404 vs 403 | 404 for non-owned resources | Prevents enumeration attacks |

---

## Outstanding Items Resolved

1. ✅ Better Auth integration strategy → Custom JWT with backend signing
2. ✅ JWT secret configuration → Single BETTER_AUTH_SECRET env var
3. ✅ Token claim structure → sub, user_id, email, iat, exp
4. ✅ Frontend token storage → localStorage
5. ✅ User isolation pattern → UserIsolationService with query scoping
6. ✅ Error response format → Constitution-defined API response structure
7. ✅ Token expiration → 24 hours, configurable via env var

---

## References

- RFC 7519 - JSON Web Token (JWT)
- OWASP Authentication Cheat Sheet
- FastAPI Security Documentation
- Better Auth Documentation (https://better-auth.com/)
- Existing codebase: `backend/src/lib/jwt_utils.py`, `backend/src/middleware/auth_middleware.py`
