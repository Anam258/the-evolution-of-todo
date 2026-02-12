# API Contract: Task Management Endpoints

**Feature**: 004-fullstack-crud-ui
**Date**: 2026-01-15
**Author**: claude

## 1. Overview

This document defines the API contract for task management operations in the Todo application. All endpoints require authentication via JWT token in the Authorization header.

## 2. Base URL and Authentication

### 2.1 Base URL
```
https://api.todo-app.com/api/tasks
```

### 2.2 Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt-token>
```

The JWT token must contain a `user_id` claim that will be used to enforce user isolation.

## 3. Common Response Format

### 3.1 Success Responses
```json
{
  "data": { /* response object */ },
  "success": true
}
```

### 3.2 Error Responses
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": { /* optional error details */ }
  },
  "success": false
}
```

## 4. Endpoint Definitions

### 4.1 GET /api/tasks
**Purpose**: Retrieve all tasks for the authenticated user

#### Request
- Method: GET
- URL: `/api/tasks`
- Headers:
  - `Authorization: Bearer <jwt-token>`
- Query Parameters:
  - `limit` (optional, integer): Number of tasks to return (default: 50, max: 100)
  - `offset` (optional, integer): Number of tasks to skip (for pagination)
  - `status` (optional, string): Filter by status ("all", "completed", "pending", default: "all")

#### Success Response (200)
```json
{
  "data": {
    "tasks": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Complete project proposal",
        "description": "Finish the project proposal document and submit for review",
        "is_completed": false,
        "created_at": "2023-10-15T10:30:00Z",
        "updated_at": "2023-10-15T10:30:00Z",
        "user_id": 123
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  },
  "success": true
}
```

#### Error Responses
- 401: Unauthorized (invalid/missing token)
- 500: Internal Server Error

#### Implementation Notes
- Only returns tasks owned by the authenticated user (user_id from JWT)
- Default sort order: newest first (by created_at)
- Implements pagination for performance

### 4.2 POST /api/tasks
**Purpose**: Create a new task for the authenticated user

#### Request
- Method: POST
- URL: `/api/tasks`
- Headers:
  - `Authorization: Bearer <jwt-token>`
  - `Content-Type: application/json`
- Body:
```json
{
  "title": "New task title",
  "description": "Optional task description"
}
```

#### Success Response (201 Created)
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "New task title",
    "description": "Optional task description",
    "is_completed": false,
    "created_at": "2023-10-15T10:30:00Z",
    "updated_at": "2023-10-15T10:30:00Z",
    "user_id": 123
  },
  "success": true
}
```

#### Error Responses
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/missing token)
- 422: Validation Error (with validation details)
- 500: Internal Server Error

#### Validation Rules
- `title` is required and must be 1-255 characters
- `description` is optional and max 1000 characters
- `is_completed` defaults to false and cannot be set via this endpoint

### 4.3 GET /api/tasks/{task_id}
**Purpose**: Retrieve a specific task for the authenticated user

#### Request
- Method: GET
- URL: `/api/tasks/{task_id}`
- Headers:
  - `Authorization: Bearer <jwt-token>`
- Path Parameters:
  - `task_id` (string): UUID of the task to retrieve

#### Success Response (200)
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project proposal",
    "description": "Finish the project proposal document and submit for review",
    "is_completed": false,
    "created_at": "2023-10-15T10:30:00Z",
    "updated_at": "2023-10-15T10:30:00Z",
    "user_id": 123
  },
  "success": true
}
```

#### Error Responses
- 401: Unauthorized (invalid/missing token)
- 404: Not Found (task doesn't exist OR not owned by user)
- 500: Internal Server Error

#### Implementation Notes
- Returns 404 if task doesn't exist OR if task is not owned by authenticated user (to prevent enumeration)

### 4.4 PUT /api/tasks/{task_id}
**Purpose**: Update a specific task for the authenticated user

#### Request
- Method: PUT
- URL: `/api/tasks/{task_id}`
- Headers:
  - `Authorization: Bearer <jwt-token>`
  - `Content-Type: application/json`
- Path Parameters:
  - `task_id` (string): UUID of the task to update
- Body:
```json
{
  "title": "Updated task title",
  "description": "Updated task description",
  "is_completed": true
}
```

#### Success Response (200)
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Updated task title",
    "description": "Updated task description",
    "is_completed": true,
    "created_at": "2023-10-15T10:30:00Z",
    "updated_at": "2023-10-15T11:45:00Z",  // Updated timestamp
    "user_id": 123
  },
  "success": true
}
```

#### Error Responses
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/missing token)
- 404: Not Found (task doesn't exist OR not owned by user)
- 422: Validation Error (with validation details)
- 500: Internal Server Error

#### Validation Rules
- `title` must be 1-255 characters if provided
- `description` must be ≤ 1000 characters if provided
- All fields are optional (partial updates allowed)

### 4.5 PATCH /api/tasks/{task_id}
**Purpose**: Update task completion status for the authenticated user

#### Request
- Method: PATCH
- URL: `/api/tasks/{task_id}`
- Headers:
  - `Authorization: Bearer <jwt-token>`
  - `Content-Type: application/json`
- Path Parameters:
  - `task_id` (string): UUID of the task to update
- Body:
```json
{
  "is_completed": true
}
```

#### Success Response (200)
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project proposal",
    "description": "Finish the project proposal document and submit for review",
    "is_completed": true,  // Updated status
    "created_at": "2023-10-15T10:30:00Z",
    "updated_at": "2023-10-15T12:00:00Z",  // Updated timestamp
    "user_id": 123
  },
  "success": true
}
```

#### Error Responses
- 400: Bad Request (invalid request body)
- 401: Unauthorized (invalid/missing token)
- 404: Not Found (task doesn't exist OR not owned by user)
- 422: Validation Error (with validation details)
- 500: Internal Server Error

#### Validation Rules
- `is_completed` is required and must be a boolean

### 4.6 DELETE /api/tasks/{task_id}
**Purpose**: Delete a specific task for the authenticated user

#### Request
- Method: DELETE
- URL: `/api/tasks/{task_id}`
- Headers:
  - `Authorization: Bearer <jwt-token>`
- Path Parameters:
  - `task_id` (string): UUID of the task to delete

#### Success Response (204 No Content)
```
(no response body)
```

#### Error Responses
- 401: Unauthorized (invalid/missing token)
- 404: Not Found (task doesn't exist OR not owned by user)
- 500: Internal Server Error

#### Implementation Notes
- Returns 204 on successful deletion
- Returns 404 if task doesn't exist OR if task is not owned by authenticated user
- Cascading delete is handled by database foreign key constraint

## 5. Security Considerations

### 5.1 User Isolation
- All endpoints verify that the authenticated user owns the accessed resources
- 404 responses instead of 403 for unauthorized access to prevent enumeration
- JWT token validation and user_id extraction in middleware

### 5.2 Input Validation
- All inputs validated using Pydantic models
- Size limits on text fields
- Type validation for all fields

### 5.3 Rate Limiting
- Authentication endpoints have rate limiting
- Other endpoints may have rate limiting based on usage patterns

## 6. Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| AUTH_001 | 401 | Invalid or missing authentication token |
| TASK_001 | 404 | Task not found or not owned by user |
| VALIDATION_001 | 422 | Validation error with field details |
| SYSTEM_001 | 500 | Internal server error |

## 7. Example Requests

### 7.1 Create Task
```bash
curl -X POST https://api.todo-app.com/api/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, bread, eggs"
  }'
```

### 7.2 Update Task Status
```bash
curl -X PATCH https://api.todo-app.com/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"is_completed": true}'
```