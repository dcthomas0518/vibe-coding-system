# Task Management System RESTful API Specification

## Overview
This document outlines the RESTful API design for a task management system that allows users to manage their personal tasks with authentication and authorization.

## Base URL
```
https://api.taskmanager.com/v1
```

## Authentication
All endpoints require authentication using Bearer tokens in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Common Headers
```
Content-Type: application/json
Accept: application/json
```

## Data Models

### Task Model
```json
{
  "id": "string (UUID)",
  "title": "string (required, max 255 chars)",
  "description": "string (optional, max 2000 chars)",
  "status": "enum (todo|in-progress|done)",
  "priority": "enum (low|medium|high)",
  "due_date": "string (ISO 8601 date-time, optional)",
  "created_at": "string (ISO 8601 date-time)",
  "updated_at": "string (ISO 8601 date-time)",
  "user_id": "string (UUID)"
}
```

### Error Response Model
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  }
}
```

## API Endpoints

### 1. Create Task
**POST** `/tasks`

Creates a new task for the authenticated user.

#### Request Body
```json
{
  "title": "Complete API documentation",
  "description": "Write comprehensive API docs for the task management system",
  "status": "todo",
  "priority": "high",
  "due_date": "2024-12-31T23:59:59Z"
}
```

#### Success Response (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete API documentation",
  "description": "Write comprehensive API docs for the task management system",
  "status": "todo",
  "priority": "high",
  "due_date": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Error Responses
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid authentication
- **422 Unprocessable Entity**: Validation errors

### 2. Get All Tasks (with filtering and pagination)
**GET** `/tasks`

Retrieves all tasks for the authenticated user with optional filtering and pagination.

#### Query Parameters
- `status` (optional): Filter by status (todo|in-progress|done)
- `priority` (optional): Filter by priority (low|medium|high)
- `due_before` (optional): Filter tasks due before this date (ISO 8601)
- `due_after` (optional): Filter tasks due after this date (ISO 8601)
- `search` (optional): Search in title and description
- `sort` (optional): Sort field (created_at|updated_at|due_date|priority) (default: created_at)
- `order` (optional): Sort order (asc|desc) (default: desc)
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)

#### Example Request
```
GET /tasks?status=todo&priority=high&page=1&limit=10&sort=due_date&order=asc
```

#### Success Response (200 OK)
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete API documentation",
      "description": "Write comprehensive API docs for the task management system",
      "status": "todo",
      "priority": "high",
      "due_date": "2024-12-31T23:59:59Z",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "total_pages": 5
  },
  "links": {
    "self": "/tasks?status=todo&priority=high&page=1&limit=10",
    "next": "/tasks?status=todo&priority=high&page=2&limit=10",
    "prev": null,
    "first": "/tasks?status=todo&priority=high&page=1&limit=10",
    "last": "/tasks?status=todo&priority=high&page=5&limit=10"
  }
}
```

### 3. Get Single Task
**GET** `/tasks/{taskId}`

Retrieves a specific task by ID.

#### Success Response (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete API documentation",
  "description": "Write comprehensive API docs for the task management system",
  "status": "todo",
  "priority": "high",
  "due_date": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Error Responses
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Task belongs to another user
- **404 Not Found**: Task not found

### 4. Update Task
**PUT** `/tasks/{taskId}`

Updates an existing task. All fields are optional in the request body.

#### Request Body
```json
{
  "title": "Complete API documentation v2",
  "status": "in-progress",
  "priority": "medium"
}
```

#### Success Response (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete API documentation v2",
  "description": "Write comprehensive API docs for the task management system",
  "status": "in-progress",
  "priority": "medium",
  "due_date": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:45:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Error Responses
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Task belongs to another user
- **404 Not Found**: Task not found
- **422 Unprocessable Entity**: Validation errors

### 5. Delete Task
**DELETE** `/tasks/{taskId}`

Deletes a specific task.

#### Success Response (204 No Content)
No response body

#### Error Responses
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Task belongs to another user
- **404 Not Found**: Task not found

### 6. Bulk Update Tasks
**PATCH** `/tasks/bulk`

Updates multiple tasks at once (e.g., mark multiple tasks as done).

#### Request Body
```json
{
  "task_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ],
  "updates": {
    "status": "done"
  }
}
```

#### Success Response (200 OK)
```json
{
  "updated": 2,
  "failed": 0,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "success": true
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "success": true
    }
  ]
}
```

## Implementation Notes

### 1. Authentication & Authorization
- Use JWT tokens for stateless authentication
- Include user_id in the JWT payload
- All database queries should filter by the authenticated user's ID
- Example middleware check:
```javascript
// Pseudo-code
if (task.user_id !== authenticatedUser.id) {
  return 403 Forbidden
}
```

### 2. Database Schema
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('todo', 'in-progress', 'done')),
    priority VARCHAR(10) NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    INDEX idx_user_status (user_id, status),
    INDEX idx_user_due_date (user_id, due_date),
    INDEX idx_user_priority (user_id, priority)
);
```

### 3. Validation Rules
- **title**: Required, 1-255 characters
- **description**: Optional, max 2000 characters
- **status**: Must be one of: todo, in-progress, done
- **priority**: Must be one of: low, medium, high
- **due_date**: Optional, must be a future date when creating

### 4. Security Considerations
- Always validate user ownership before any operation
- Use parameterized queries to prevent SQL injection
- Implement rate limiting (e.g., 100 requests per minute per user)
- Sanitize all input data
- Use HTTPS for all communications
- Implement CORS properly for web clients

### 5. Performance Optimizations
- Add database indexes on frequently queried fields (user_id, status, due_date)
- Implement caching for frequently accessed tasks
- Use database connection pooling
- Consider implementing cursor-based pagination for large datasets
- Add response compression (gzip)

### 6. Error Handling
Consistent error response format:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "title": "Title is required",
      "due_date": "Due date must be in the future"
    }
  }
}
```

Common error codes:
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Access denied
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Input validation failed
- `INTERNAL_ERROR`: Server error

### 7. API Versioning
- Version in URL path (e.g., /v1/tasks)
- Support backwards compatibility
- Deprecation notices in headers for old versions
- Clear migration guides for breaking changes

### 8. Additional Features to Consider
- Task categories/tags
- Task attachments
- Task comments
- Recurring tasks
- Task sharing/collaboration
- Webhooks for task events
- Batch operations
- Export functionality (CSV, JSON)

## Example Implementation (Node.js/Express)

```javascript
// Example route handler for GET /tasks
app.get('/v1/tasks', authenticate, async (req, res) => {
  try {
    const {
      status,
      priority,
      due_before,
      due_after,
      search,
      sort = 'created_at',
      order = 'desc',
      page = 1,
      limit = 20
    } = req.query;

    // Build query
    let query = Task.where('user_id', req.user.id);
    
    if (status) query = query.where('status', status);
    if (priority) query = query.where('priority', priority);
    if (due_before) query = query.where('due_date', '<', due_before);
    if (due_after) query = query.where('due_date', '>', due_after);
    if (search) {
      query = query.where(function() {
        this.where('title', 'LIKE', `%${search}%`)
            .orWhere('description', 'LIKE', `%${search}%`);
      });
    }

    // Pagination
    const offset = (page - 1) * limit;
    const total = await query.clone().count();
    
    // Get results
    const tasks = await query
      .orderBy(sort, order)
      .limit(limit)
      .offset(offset)
      .select();

    // Build response
    res.json({
      data: tasks,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        total_pages: Math.ceil(total / limit)
      },
      links: buildPaginationLinks(req, page, limit, total)
    });
  } catch (error) {
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'An error occurred while fetching tasks'
      }
    });
  }
});
```

## Testing Considerations
- Unit tests for all validation logic
- Integration tests for all endpoints
- Load testing for pagination performance
- Security testing for authorization checks
- End-to-end tests for critical user flows