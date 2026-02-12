---
name: auth-skill
description: Implement secure authentication systems including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Registration (Signup)**
   - Accept email/username and password
   - Validate input (required fields, format)
   - Hash passwords before storing
   - Prevent duplicate accounts

2. **User Login (Signin)**
   - Verify user credentials
   - Compare hashed passwords securely
   - Handle invalid login attempts
   - Return authentication token on success

3. **Password Security**
   - Use strong hashing algorithms (bcrypt, argon2)
   - Never store plain-text passwords
   - Use proper salt and cost factors
   - Support password updates and resets

4. **JWT Authentication**
   - Generate JWT tokens on successful login
   - Include user ID and roles in payload
   - Set token expiration time
   - Verify tokens for protected routes

5. **Better Auth Integration**
   - Configure Better Auth providers
   - Use secure session or token handling
   - Integrate with existing backend framework
   - Support scalable auth workflows

## Best Practices
- Always hash passwords
- Use HTTPS for auth endpoints
- Keep JWT secrets secure
- Short-lived access tokens
- Separate auth logic from business logic
- Follow OWASP authentication guidelines

## Example Structure

```ts
// signup.ts
import bcrypt from "bcrypt";

const hashedPassword = await bcrypt.hash(password, 12);

// signin.ts
import jwt from "jsonwebtoken";

const token = jwt.sign(
  { userId: user.id },
  process.env.JWT_SECRET,
  { expiresIn: "1h" }
);