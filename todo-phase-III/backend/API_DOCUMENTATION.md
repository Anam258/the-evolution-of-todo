# Todo API Documentation

## Authentication Endpoints

This API uses JWT-based authentication. All protected endpoints require a valid JWT token in the Authorization header.

### Base URL
`http://localhost:8000/api/v1` (Development)
`https://api.yourapp.com/api/v1` (Production)

### Authentication Headers
All protected endpoints require the following header:
```
Authorization: Bearer {jwt_token}
```

---

## User Registration

### POST /auth/register

Register a new user account.

#### Request
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

#### Response (Success)
```json
{
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### Response (Error)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "User with this email already exists"
  }
}
```

#### Rate Limiting
- Maximum: 2 registrations per hour per IP address
- Exceeding limit returns HTTP 429 Too Many Requests

---

## User Login

### POST /auth/login

Authenticate user and receive JWT token.

#### Request
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

#### Response (Success)
```json
{
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### Response (Error - Invalid Credentials)
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Incorrect email or password"
  }
}
```

#### Response (Error - Rate Limited)
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many login attempts. Please try again later."
  }
}
```

#### Rate Limiting
- Maximum: 5 login attempts per 15 minutes per IP address
- Exceeding limit returns HTTP 429 Too Many Requests

---

## User Logout

### POST /auth/logout

Logout user (client-side token removal is sufficient for JWT).

#### Response
```json
{
  "message": "Successfully logged out"
}
```

---

## Get Current User Information

### GET /auth/me

Get information about the currently authenticated user.

#### Headers
```
Authorization: Bearer {valid_jwt_token}
```

#### Response (Success)
```json
{
  "data": {
    "user_id": 1,
    "email": "user@example.com"
  }
}
```

#### Response (Unauthorized)
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Could not validate credentials"
  }
}
```

---

## Health Check

### GET /health

Check the health status of the API.

#### Response
```json
{
  "status": "healthy",
  "service": "todo-api"
}
```

---

## Security Headers

All API responses include the following security headers:

- `X-Content-Type-Options: nosniff` - Prevents MIME-type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - Enables XSS protection in older browsers
- `Referrer-Policy: strict-origin-when-cross-origin` - Controls referrer information
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` - Enforces HTTPS
- `X-DNS-Prefetch-Control: off` - Disables DNS prefetching
- `X-Download-Options: noopen` - Disables external resource loading in IE

---

## Error Codes

The API uses the following error codes:

- `UNAUTHORIZED (401)`: Missing, invalid, or expired authentication token
- `FORBIDDEN (403)`: User authenticated but lacks permission (not used for user isolation)
- `NOT_FOUND (404)`: Resource not found OR not owned by user (for user isolation)
- `VALIDATION_ERROR (422)`: Request data validation failed
- `RATE_LIMIT_EXCEEDED (429)`: Rate limit exceeded
- `INTERNAL_ERROR (500)`: Server error occurred

---

## JWT Token Claims

The JWT token contains the following claims:

- `user_id`: The authenticated user's ID (required)
- `email`: The authenticated user's email (optional)
- `exp`: Expiration timestamp (Unix timestamp)
- `iat`: Issued at timestamp (Unix timestamp)
- `sub`: Subject identifier (same as user_id)

Token expires after 24 hours by default.

---

## User Isolation

All protected endpoints enforce user isolation. When a user attempts to access resources that belong to another user, the API returns a 404 Not Found error instead of a 403 Forbidden error to prevent enumeration attacks.