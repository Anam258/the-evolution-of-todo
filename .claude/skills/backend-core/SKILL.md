name: backend-core
description: Design and implement backend APIs by generating routes, handling requests/responses, and connecting to databases.
---

# Backend Core Skill

## Instructions

1. **Routing**
   - Define RESTful routes (GET, POST, PUT/PATCH, DELETE)
   - Use clear and consistent URL structures
   - Group routes by resource (e.g. `/users`, `/tasks`)

2. **Request Handling**
   - Parse request parameters, query strings, and body data
   - Validate input data before processing
   - Handle authentication and authorization if required

3. **Response Handling**
   - Return proper HTTP status codes (200, 201, 400, 401, 404, 500)
   - Send structured JSON responses
   - Include meaningful error messages

4. **Database Integration**
   - Connect to a database (SQLite, PostgreSQL, MongoDB, etc.)
   - Perform CRUD operations using models or queries
   - Handle connection errors and edge cases

## Best Practices
- Follow REST API conventions
- Keep controllers thin and logic modular
- Validate and sanitize all user input
- Never expose sensitive data in responses
- Use environment variables for DB credentials

## Example Structure

```js
// routes/tasks.js
import express from "express";
import { getTasks, createTask } from "../controllers/taskController.js";

const router = express.Router();

router.get("/", getTasks);
router.post("/", createTask);

export default router;