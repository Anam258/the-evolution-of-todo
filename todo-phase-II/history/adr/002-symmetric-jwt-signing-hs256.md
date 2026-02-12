# ADR-002: Symmetric JWT Signing (HS256) vs Asymmetric Keys (RS256)

## Status
Accepted

## Date
2026-01-16

## Context
The team needed to decide on the cryptographic approach for JWT signing in the authentication system. The choice between symmetric (HS256) and asymmetric (RS256) algorithms had implications for key management, cross-service authentication, and security posture.

## Decision
We will use symmetric HS256 algorithm with a shared secret (BETTER_AUTH_SECRET) for JWT signing, rather than asymmetric RS256 with public/private key pairs.

## Alternatives Considered
1. **Asymmetric RS256**: Use RSA public/private key pairs for signing
   - Pros: Better key distribution (public keys can be shared freely), more suitable for distributed systems
   - Cons: More complex key management, slower cryptographic operations, unnecessary complexity for single-tenant app

2. **Symmetric HS256 (Selected)**: Use shared secret with HMAC SHA-256
   - Pros: Simpler implementation, faster operations, adequate security for shared secret scenario
   - Cons: Requires secure secret distribution, same secret on all services

3. **Elliptic Curve ES256**: Use ECDSA with P-256 curve
   - Pros: Good security with smaller keys, efficient operations
   - Cons: Less widely supported, adds complexity without clear benefit for this use case

## Rationale
- Simpler implementation and maintenance for the MVP
- Adequate security when combined with HTTPS transport
- Faster cryptographic operations compared to asymmetric algorithms
- Suitable for a single-tenant application where the secret can be securely shared between frontend and backend
- Aligns with the team's current operational capabilities
- Lower computational overhead per authentication request

## Consequences
- Need for secure distribution and storage of the shared secret
- All services must have access to the same secret
- Secret rotation requires coordination across all services
- Adequate security for the current threat model but may require reevaluation for future scaling