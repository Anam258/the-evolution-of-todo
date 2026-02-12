# Data Model: Backend Connectivity and Startup Fixes

## Overview
This feature focuses on fixing backend connectivity and startup issues. Since this is an infrastructure/configuration fix rather than a data model change, there are no new entities to define. However, the existing authentication configuration requires proper environment variable loading.

## Key Entities

### Environment Configuration
- **Type**: Configuration entity
- **Description**: Application settings stored in .env file including secrets, ports, and database connections
- **Attributes**:
  - BETTER_AUTH_SECRET: String (required, min 32 characters)
  - DATABASE_URL: String (PostgreSQL connection string)
  - JWT_ALGORITHM: String (default: HS256)
  - JWT_EXPIRATION_DELTA: Integer (default: 1440 minutes)
  - ALLOWED_ORIGINS: String (comma-separated origins)
  - PORT: Integer (default: 8000)

### Authentication Secrets
- **Type**: Security entity
- **Description**: Secure tokens and keys required for the Better Auth system to function properly
- **Attributes**:
  - SecretKey: String (the BETTER_AUTH_SECRET value)
  - Algorithm: String (JWT algorithm for signing)
  - ExpirationTime: Integer (token expiration in minutes)

## Validation Rules
- BETTER_AUTH_SECRET must be at least 32 characters long
- DATABASE_URL must be a valid PostgreSQL connection string
- PORT must be a valid available port number
- JWT_ALGORITHM must be one of: HS256, HS384, HS512

## Relationships
None required for this fix - this is a configuration validation and startup issue resolution.