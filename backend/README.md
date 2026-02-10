# Todo API Backend with JWT Authentication

This is the backend API for the Todo application with JWT-based authentication and user isolation.

## Authentication System Documentation

### Overview
The authentication system implements JWT-based authentication with the following key features:

1. **JWT Token Management**: Secure token generation, verification, and expiration handling
2. **User Isolation**: All user data is isolated by user ID to prevent cross-user access
3. **Rate Limiting**: Protection against brute force attacks on authentication endpoints
4. **Input Validation**: Comprehensive validation of all user inputs
5. **Security Headers**: Multiple security headers to protect against common web vulnerabilities
6. **Monitoring**: Health check and metrics endpoints for system monitoring

### Authentication Flow
1. User registers via `POST /auth/register`
2. User logs in via `POST /auth/login` to obtain JWT token
3. JWT token is included in `Authorization: Bearer <token>` header for protected endpoints
4. Backend verifies token and extracts user_id for user isolation
5. All database queries are scoped to the authenticated user_id

### Security Features
- **JWT-based authentication** with HS256 algorithm
- **User isolation**: All user data is scoped to the authenticated user
- **Rate limiting**: Maximum 5 login attempts per 15 minutes per IP
- **Rate limiting**: Maximum 2 registrations per hour per IP
- **Input validation**: Email format validation and strong password requirements
- **Security headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, etc.
- **Proper error handling**: 404 instead of 403 for unauthorized resource access to prevent enumeration

### Environment Variables

The following environment variables are required for the application to run properly:

#### Authentication Configuration
- `BETTER_AUTH_SECRET` (required): Secret key used for JWT signing and verification. Must be at least 32 characters long.
- `JWT_ALGORITHM` (optional): Algorithm used for JWT signing (default: `HS256`). Supported values: `HS256`, `HS384`, `HS512`.
- `JWT_EXPIRATION_DELTA` (optional): Token expiration time in seconds (default: `86400` for 24 hours).

#### Database Configuration
- `DATABASE_URL` (required): Connection string for the PostgreSQL database.

#### Application Configuration
- `ALLOWED_ORIGINS` (optional): Comma-separated list of allowed origins for CORS (default: `http://localhost:3000`).
- `PORT` (optional): Port number for the application to listen on (default: `8000`).
- `DEBUG` (optional): Enable debug mode (default: `False`).

## Setup

1. Copy `.env.example` to `.env` and fill in the required values:
   ```bash
   cp .env.example .env
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the application:
   ```bash
   python -m src.main
   ```
   Or with uvicorn directly:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Authenticate user and get JWT token
- `POST /auth/logout` - Logout user (client-side token removal)
- `GET /auth/me` - Get current authenticated user's information

### Health Check
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint

## Security Features

- JWT-based authentication with HS256 algorithm
- User isolation: All user data is scoped to the authenticated user
- Proper error handling that prevents user enumeration
- Secure password hashing with bcrypt

## Cross-Service Token Validation

This backend expects tokens to be generated with the same `BETTER_AUTH_SECRET` as configured in the frontend. The application will verify at startup that the secret is properly configured and of sufficient length. If there's a mismatch between the secret used to generate tokens and the one used to verify them, authentication will fail.

To test cross-service compatibility, you can run the startup validation which creates a test token and verifies it.