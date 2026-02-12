# ADR-003: localStorage Token Storage vs HttpOnly Cookies

## Status
Accepted

## Date
2026-01-16

## Context
The team needed to decide how to store JWT tokens on the frontend for the authentication system. The choice between localStorage and HttpOnly cookies had implications for security, cross-site scripting (XSS) protection, and cross-site request forgery (CSRF) prevention.

## Decision
We will store JWT tokens in localStorage for the MVP, rather than using HttpOnly cookies with CSRF tokens.

## Alternatives Considered
1. **HttpOnly Cookies with CSRF Protection**: Store tokens in HttpOnly cookies and implement CSRF tokens
   - Pros: Protection against XSS token theft, automatic inclusion in requests
   - Cons: More complex implementation, requires CSRF handling, additional server-side state

2. **localStorage (Selected)**: Store tokens in browser localStorage
   - Pros: Simple implementation, easy token access for API requests, transparent to developers
   - Cons: Vulnerable to XSS if application has XSS vulnerabilities

3. **sessionStorage**: Store tokens in browser sessionStorage
   - Pros: Similar to localStorage but cleared on tab close
   - Cons: Poor user experience (tokens lost on tab refresh), same XSS vulnerabilities as localStorage

4. **Memory-only storage**: Store tokens only in JavaScript memory
   - Pros: No persistent storage, XSS exposure limited to session
   - Cons: Poor user experience (tokens lost on page refresh), requires re-authentication

## Rationale
- Simpler implementation for the MVP timeline
- Better developer experience with easier token access
- Transparent to the development team who are familiar with this pattern
- XSS vulnerabilities should be prevented through React's default escaping and proper input validation
- Allows for explicit control over token lifecycle and error handling
- Aligns with the current architecture and team's operational approach

## Consequences
- Increased risk of token theft if the application has XSS vulnerabilities
- Need for stronger focus on preventing XSS vulnerabilities in the frontend
- Tokens persist across browser sessions (until explicit logout or expiration)
- Manual token inclusion in API requests rather than automatic via browser
- May require reevaluation for production security requirements