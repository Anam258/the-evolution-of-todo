# ADR-001: Custom JWT Implementation vs Better Auth Sessions

## Status
Accepted

## Date
2026-01-16

## Context
The team needed to decide between implementing a custom JWT-based authentication system and using Better Auth's default session management for the multi-user Todo application. The decision had implications for session management strategy, cross-service authentication, and the overall security architecture.

## Decision
We will implement a custom JWT-based authentication system using python-jose on the backend and manual token handling on the frontend, rather than using Better Auth's default database session management.

## Alternatives Considered
1. **Pure Better Auth sessions**: Use Better Auth's built-in session management with database-stored sessions
   - Pros: Less custom code, battle-tested library, automatic session management
   - Cons: Requires server-side session storage, not pure stateless JWT, couples frontend and backend more tightly

2. **Better Auth with JWT plugin**: Use Better Auth's JWT plugin capability
   - Pros: Leverages Better Auth ecosystem, some standardization benefits
   - Cons: Less transparency into token structure, potential vendor lock-in

3. **Custom JWT implementation (Selected)**: Implement JWT handling with python-jose and manual frontend handling
   - Pros: Explicit control over token claims, truly stateless, transparent implementation
   - Cons: More custom code, requires more security considerations

## Rationale
- The custom JWT approach provides explicit control over token claims (user_id, email, iat, exp)
- Enables truly stateless authentication without server-side session storage
- Provides transparency in the authentication flow for easier debugging and maintenance
- Aligns with the microservices architecture requirements of the application
- Allows for precise user isolation at the database query level

## Consequences
- More custom code to maintain and secure
- Need for careful attention to JWT security best practices
- Explicit responsibility for token lifecycle management
- Greater flexibility in token structure and validation logic