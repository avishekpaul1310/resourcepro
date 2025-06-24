# ResourcePro API Documentation

## Overview

ResourcePro provides a comprehensive REST API for enterprise integration, allowing external applications to manage resources, projects, tasks, and assignments programmatically.

**Base URL:** `http://your-domain.com/api/`  
**API Version:** `v1`  
**Authentication:** Token-based  

## Features

- 🔐 **Secure Authentication** - Token-based API authentication
- 📚 **Comprehensive Resources** - Full CRUD operations for all entities
- 🤖 **AI Integration** - AI-powered resource allocation and recommendations
- 📄 **Auto Documentation** - Interactive Swagger/OpenAPI documentation
- 🔍 **Advanced Filtering** - Powerful search and filtering capabilities
- 🔒 **Permission System** - Role-based access control
- 🌐 **CORS Support** - Cross-origin resource sharing for web applications

## Quick Start

### 1. Authentication

First, obtain an API token:

```bash
curl -X POST http://your-domain.com/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Response:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "your_username",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

### 2. Making API Calls

Include the token in the Authorization header:

```bash
curl -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  http://your-domain.com/api/v1/resources/
```

## API Endpoints

### Resources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/resources/` | List all resources |
| POST | `/api/v1/resources/` | Create a new resource |
| GET | `/api/v1/resources/{id}/` | Get resource details |
| PUT | `/api/v1/resources/{id}/` | Update resource |
| DELETE | `/api/v1/resources/{id}/` | Delete resource |
| GET | `/api/v1/resources/{id}/utilization/` | Get resource utilization |
| GET | `/api/v1/resources/available/` | Get available resources |

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/` | List all projects |
| POST | `/api/v1/projects/` | Create a new project |
| GET | `/api/v1/projects/{id}/` | Get project details |
| PUT | `/api/v1/projects/{id}/` | Update project |
| DELETE | `/api/v1/projects/{id}/` | Delete project |
| GET | `/api/v1/projects/{id}/statistics/` | Get project statistics |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks/` | List all tasks |
| POST | `/api/v1/tasks/` | Create a new task |
| GET | `/api/v1/tasks/{id}/` | Get task details |
| PUT | `/api/v1/tasks/{id}/` | Update task |
| DELETE | `/api/v1/tasks/{id}/` | Delete task |
| GET | `/api/v1/tasks/unassigned/` | Get unassigned tasks |
| GET | `/api/v1/tasks/{id}/ai_suggestions/` | Get AI resource suggestions |

### Assignments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/assignments/` | List all assignments |
| POST | `/api/v1/assignments/` | Create an assignment |
| GET | `/api/v1/assignments/{id}/` | Get assignment details |
| PUT | `/api/v1/assignments/{id}/` | Update assignment |
| DELETE | `/api/v1/assignments/{id}/` | Delete assignment |
| POST | `/api/v1/assignments/bulk_assign/` | Bulk assign tasks |
| GET | `/api/v1/assignments/check_conflicts/` | Check assignment conflicts |

### Skills

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/skills/` | List all skills |
| POST | `/api/v1/skills/` | Create a new skill |
| GET | `/api/v1/skills/{id}/` | Get skill details |
| PUT | `/api/v1/skills/{id}/` | Update skill |
| DELETE | `/api/v1/skills/{id}/` | Delete skill |

### Time Entries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/time-entries/` | List time entries |
| POST | `/api/v1/time-entries/` | Create time entry |
| GET | `/api/v1/time-entries/{id}/` | Get time entry details |
| PUT | `/api/v1/time-entries/{id}/` | Update time entry |
| DELETE | `/api/v1/time-entries/{id}/` | Delete time entry |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/` | List all users |
| GET | `/api/v1/users/{id}/` | Get user details |
| GET | `/api/v1/users/me/` | Get current user profile |

## Filtering and Search

### Query Parameters

All list endpoints support filtering, searching, and ordering:

```bash
# Filter resources by role
GET /api/v1/resources/?role=Developer

# Search resources by name
GET /api/v1/resources/?search=john

# Order resources by capacity
GET /api/v1/resources/?ordering=capacity

# Combine filters
GET /api/v1/resources/?role=Developer&department=Engineering&ordering=-capacity
```

### Available Filters

#### Resources
- `name`, `role`, `department`, `skills`, `timezone`, `location`
- `min_capacity`, `max_capacity`, `min_cost`, `max_cost`

#### Projects
- `name`, `status`, `priority`, `manager`
- `start_date_after`, `start_date_before`, `end_date_after`, `end_date_before`
- `min_budget`, `max_budget`

#### Tasks
- `name`, `project`, `project_name`, `status`, `priority`, `skills_required`
- `start_date_after`, `start_date_before`, `end_date_after`, `end_date_before`
- `min_estimated_hours`, `max_estimated_hours`, `is_assigned`

#### Assignments
- `resource`, `resource_name`, `task`, `task_name`, `project`, `project_name`
- `min_allocated_hours`, `max_allocated_hours`

## Pagination

All list endpoints are paginated. Default page size is 50 items.

```json
{
  "count": 123,
  "next": "http://your-domain.com/api/v1/resources/?page=2",
  "previous": null,
  "results": [...]
}
```

Control pagination with query parameters:
- `page`: Page number
- `page_size`: Items per page (max 100)

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

Error responses include details:

```json
{
  "detail": "Invalid input.",
  "errors": {
    "name": ["This field is required."],
    "email": ["Enter a valid email address."]
  }
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:
- **Authenticated users**: 1000 requests/hour
- **Anonymous users**: 100 requests/hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## Interactive Documentation

Visit these URLs for interactive API documentation:

- **Swagger UI**: `http://your-domain.com/api/docs/`
- **ReDoc**: `http://your-domain.com/api/redoc/`
- **OpenAPI Schema**: `http://your-domain.com/api/schema/`

## AI Features

### Get Resource Suggestions

Get AI-powered resource allocation suggestions for a task:

```bash
GET /api/v1/tasks/{task_id}/ai_suggestions/
```

Response:
```json
{
  "task_id": 1,
  "task_name": "Implement user authentication",
  "suggestions": [
    {
      "resource": {
        "id": 1,
        "name": "John Doe",
        "role": "Senior Developer"
      },
      "match_score": 0.95,
      "reasoning": "Perfect skill match for authentication systems",
      "skill_match": {
        "required": ["Python", "Django", "Security"],
        "matched": ["Python", "Django", "Security"],
        "missing": []
      },
      "availability_status": "Available",
      "utilization_impact": 75.5
    }
  ]
}
```

### Bulk Assignment

Automatically assign multiple tasks using AI:

```bash
POST /api/v1/assignments/bulk_assign/
Content-Type: application/json

{
  "task_ids": [1, 2, 3, 4, 5],
  "auto_assign": true,
  "force_reassign": false
}
```

## CORS Support

CORS is configured to allow cross-origin requests from web applications:

```javascript
// JavaScript example
fetch('http://your-domain.com/api/v1/resources/', {
  method: 'GET',
  headers: {
    'Authorization': 'Token your-token-here',
    'Content-Type': 'application/json',
  },
})
.then(response => response.json())
.then(data => console.log(data));
```

## WebSocket Support

Real-time updates are available via WebSocket connections:

```javascript
const ws = new WebSocket('ws://your-domain.com/ws/api/updates/');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

## SDKs and Libraries

### Python SDK

```python
import requests

class ResourceProAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {'Authorization': f'Token {token}'}
    
    def get_resources(self, **filters):
        response = requests.get(
            f'{self.base_url}/api/v1/resources/',
            headers=self.headers,
            params=filters
        )
        return response.json()
    
    def create_assignment(self, task_id, resource_id, allocated_hours):
        data = {
            'task_id': task_id,
            'resource_id': resource_id,
            'allocated_hours': allocated_hours
        }
        response = requests.post(
            f'{self.base_url}/api/v1/assignments/',
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage
api = ResourceProAPI('http://your-domain.com', 'your-token-here')
resources = api.get_resources(role='Developer')
```

### JavaScript SDK

```javascript
class ResourceProAPI {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json',
    };
  }

  async getResources(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(
      `${this.baseUrl}/api/v1/resources/?${params}`,
      { headers: this.headers }
    );
    return response.json();
  }

  async createAssignment(taskId, resourceId, allocatedHours) {
    const response = await fetch(`${this.baseUrl}/api/v1/assignments/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        task_id: taskId,
        resource_id: resourceId,
        allocated_hours: allocatedHours,
      }),
    });
    return response.json();
  }
}

// Usage
const api = new ResourceProAPI('http://your-domain.com', 'your-token-here');
const resources = await api.getResources({ role: 'Developer' });
```

## Support

For API support and questions:
- Email: api-support@yourcompany.com
- Documentation: http://your-domain.com/api/docs/
- Status Page: http://status.yourcompany.com
