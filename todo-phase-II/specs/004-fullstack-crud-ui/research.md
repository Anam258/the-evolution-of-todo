# Research Findings: Full-Stack CRUD Features and Responsive UI Integration

**Feature**: 004-fullstack-crud-ui
**Date**: 2026-01-15
**Author**: claude

## 1. API Endpoint Design

### Decision: Standard RESTful endpoints with user scoping
Based on the existing authentication system and best practices, we'll use `/api/tasks` as the base path with JWT-based user scoping rather than `/api/{user_id}/tasks`.

### Rationale:
- The authentication middleware will extract user_id from JWT, eliminating the need to pass it in the URL
- Clean, standard RESTful API design
- Consistent with typical FastAPI patterns
- User isolation is handled at the middleware/database level

### Alternatives considered:
- `/api/{user_id}/tasks` - Requires passing user_id in URL (exposes user identifiers)
- `/api/my/tasks` - Less standard convention
- `/api/user/tasks` - Could work but "tasks" is more RESTful

## 2. Database Schema

### Decision: Extend existing User model with Task model having user_id foreign key
We'll create a Task model that includes a foreign key to the User model for proper user isolation.

### Rationale:
- Maintains referential integrity
- Enables efficient querying with joins
- Supports the user isolation requirement
- Follows SQLModel best practices

### Task Model Definition:
```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE")

    # Relationship back to user if needed
    user: Optional[User] = Relationship(back_populates="tasks")
```

### Alternatives considered:
- Storing user_id as a simple string field without foreign key (loses referential integrity)
- Using a different primary key structure (UUID is standard for distributed systems)

## 3. Frontend Architecture

### Decision: Component-based architecture with Next.js App Router
Organize the frontend with reusable components and proper separation of concerns.

### Rationale:
- Next.js App Router is the modern standard
- Component-based architecture promotes reusability
- Clear separation between presentation and data fetching
- Follows React best practices

### Component Structure:
- `src/app/dashboard/page.tsx` - Main dashboard page
- `src/components/todo/TodoList.tsx` - Displays list of tasks
- `src/components/todo/TodoItem.tsx` - Individual task component with actions
- `src/components/todo/CreateTodoForm.tsx` - Form for creating new tasks
- `src/components/ui/ToastProvider.tsx` - Global toast notification provider
- `src/lib/api-client.ts` - Centralized API client
- `src/hooks/useTodos.ts` - Custom hook for todo operations

### Alternatives considered:
- Monolithic page components (harder to maintain)
- Different routing patterns (App Router is the current standard)

## 4. JWT Token Structure

### Decision: Use existing Better Auth JWT structure
Leverage the existing JWT implementation from feature 003-better-auth-jwt which should contain user_id in the payload.

### Rationale:
- Consistency with existing authentication system
- No need to reinvent authentication mechanisms
- Leverages tested and secure implementation
- Maintains user session state properly

### Expected JWT Payload:
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Authentication Flow:
1. Frontend uses Better Auth to manage user sessions
2. API requests include Authorization: Bearer {token} header
3. Backend middleware verifies JWT and extracts user_id
4. Database queries are automatically scoped by user_id

### Alternatives considered:
- Custom JWT implementation (unnecessary complexity)
- Session-based authentication (doesn't fit RESTful API pattern)

## 5. API Error Handling Best Practices

### Decision: Standard HTTP status codes with structured error responses
Follow RESTful API best practices for error handling.

### Rationale:
- Standardized approach that clients can reliably handle
- Clear distinction between different types of errors
- Consistent with existing API patterns
- Good for debugging and monitoring

### Error Response Format:
```json
{
  "detail": "Human-readable error message",
  "status_code": 401,
  "error_code": "AUTHENTICATION_ERROR"
}
```

### Status Codes:
- 200: Success for GET, PUT, PATCH
- 201: Success for POST (resource created)
- 204: Success for DELETE (no content)
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/missing token)
- 404: Not Found (resource not found OR not owned by user)
- 422: Validation Error (with details)
- 500: Internal Server Error

### Alternatives considered:
- Custom status code system (not standard)
- Different error response formats (not consistent with FastAPI defaults)

## 6. Data Fetching Patterns

### Decision: Hybrid approach with server-side rendering for initial load and client-side for updates
Use Next.js strengths for both initial data loading and dynamic updates.

### Rationale:
- Server-side rendering provides SEO benefits and initial load performance
- Client-side updates provide responsive UI without full page reloads
- Caching strategies can be implemented appropriately
- Follows Next.js best practices

### Implementation:
- Server Components for initial task list (authenticated user context)
- Client Components for interactive elements (toggle, edit, delete)
- SWR or React Query for client-side data fetching and caching
- Optimistic updates for better user experience

### Alternatives considered:
- Pure client-side fetching (slower initial load)
- Pure server-side approach (less interactive experience)

## 7. Responsive Design with Tailwind CSS

### Decision: Mobile-first approach with responsive utility classes
Implement responsive design using Tailwind's breakpoint system.

### Rationale:
- Mobile-first approach ensures good mobile experience
- Tailwind's utility classes provide flexibility
- Consistent design language across components
- Well-documented and widely adopted approach

### Breakpoints:
- sm: 640px (mobile)
- md: 768px (tablet)
- lg: 1024px (desktop)
- xl: 1280px (large desktop)

### Layout Strategy:
- Single column on mobile
- Two columns on tablet
- Three columns on desktop (if appropriate)
- Touch-friendly controls on all devices

### Alternatives considered:
- Custom CSS classes (more maintenance)
- Different CSS framework (Tailwind already integrated)

## 8. Toast Notification Implementation

### Decision: Custom toast system with React context
Implement a toast notification system using React Context and Tailwind CSS.

### Rationale:
- Full control over appearance and behavior
- Lightweight solution without external dependencies
- Consistent with Tailwind styling approach
- Can be customized for specific needs

### Implementation:
- ToastContext for managing toast state
- ToastProvider wrapper component
- Individual toast components with auto-dismiss
- Support for different toast types (success, error, warning)

### Alternatives considered:
- Third-party libraries like react-hot-toast (adds dependencies)
- Browser native notifications (limited styling options)