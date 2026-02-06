# PM Agentic Workflow - API Documentation

Complete API documentation for integrating with the PM Agentic Workflow backend.

## Base URL
- **Local**: `http://localhost:8000`
- **Production**: Set in Render dashboard

## Authentication
Currently no authentication required. Add `Authorization: Bearer <token>` header for future JWT implementation.

---

## Health & Info

### GET /health
Check if the service is running.

**Response**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

### GET /
API information.

**Response**
```json
{
  "message": "PM Agentic Workflow API",
  "docs": "/docs",
  "health": "/health"
}
```

---

## Projects

### POST /api/v1/projects/
Create a new project.

**Request Body**
```json
{
  "name": "My Project",
  "description": "Project description",
  "owner_id": "user_001",
  "team_members": ["user_001", "user_002"],
  "start_date": "2024-01-15T00:00:00Z",
  "target_end_date": "2024-03-15T00:00:00Z"
}
```

**Response** `201 Created`
```json
{
  "id": "65f8a1b2c3d4e5f6a7b8c9d0",
  "message": "Project created successfully"
}
```

---

### GET /api/v1/projects/
List all projects.

**Query Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | int | 0 | Pagination offset |
| limit | int | 20 | Max results |
| active_only | bool | true | Filter active projects |

**Response** `200 OK`
```json
[
  {
    "_id": "65f8a1b2c3d4e5f6a7b8c9d0",
    "name": "My Project",
    "description": "Project description",
    "owner_id": "user_001",
    "team_members": ["user_001", "user_002"],
    "is_active": true,
    "created_at": "2024-01-15T00:00:00Z",
    "updated_at": "2024-01-15T00:00:00Z"
  }
]
```

---

### GET /api/v1/projects/{project_id}
Get a specific project.

**Response** `200 OK`
```json
{
  "_id": "65f8a1b2c3d4e5f6a7b8c9d0",
  "name": "My Project",
  "description": "Project description",
  "owner_id": "user_001",
  "team_members": ["user_001", "user_002"],
  "start_date": "2024-01-15T00:00:00Z",
  "target_end_date": "2024-03-15T00:00:00Z",
  "is_active": true,
  "created_at": "2024-01-15T00:00:00Z",
  "updated_at": "2024-01-15T00:00:00Z"
}
```

---

### PATCH /api/v1/projects/{project_id}
Update a project.

**Request Body** (all fields optional)
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "team_members": ["user_001", "user_002", "user_003"],
  "target_end_date": "2024-04-15T00:00:00Z"
}
```

**Response** `200 OK`
```json
{
  "message": "Project updated successfully"
}
```

---

### DELETE /api/v1/projects/{project_id}
Soft delete a project (sets `is_active` to false).

**Response** `200 OK`
```json
{
  "message": "Project deleted successfully"
}
```

---

### GET /api/v1/projects/{project_id}/state
Get full project state including all related entities. **This is the input format for agents.**

**Response** `200 OK`
```json
{
  "project": { ... },
  "tasks": [ ... ],
  "milestones": [ ... ],
  "risks": [ ... ],
  "recent_events": [ ... ]
}
```

---

## Tasks

### POST /api/v1/projects/{project_id}/tasks/
Create a task.

**Request Body**
```json
{
  "title": "Implement feature X",
  "description": "Detailed description",
  "status": "pending",
  "assignee_id": "user_001",
  "priority": 2,
  "due_date": "2024-02-01T00:00:00Z",
  "dependencies": [],
  "labels": ["backend", "feature"],
  "milestone_id": "65f8a1b2c3d4e5f6a7b8c9d1"
}
```

**Status Values**: `pending`, `in_progress`, `blocked`, `in_review`, `completed`, `cancelled`

**Priority**: 1 (highest) to 5 (lowest)

**Response** `201 Created`
```json
{
  "id": "65f8a1b2c3d4e5f6a7b8c9d2",
  "message": "Task created successfully"
}
```

---

### GET /api/v1/projects/{project_id}/tasks/
List tasks in a project.

**Query Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| status_filter | string | Filter by status |
| assignee_id | string | Filter by assignee |
| skip | int | Pagination offset |
| limit | int | Max results (default 50) |

**Response** `200 OK`
```json
[
  {
    "_id": "65f8a1b2c3d4e5f6a7b8c9d2",
    "project_id": "65f8a1b2c3d4e5f6a7b8c9d0",
    "title": "Implement feature X",
    "status": "in_progress",
    "assignee_id": "user_001",
    "priority": 2,
    "due_date": "2024-02-01T00:00:00Z",
    "dependencies": [],
    "labels": ["backend", "feature"],
    "created_at": "2024-01-15T00:00:00Z",
    "updated_at": "2024-01-16T00:00:00Z"
  }
]
```

---

### PATCH /api/v1/projects/{project_id}/tasks/{task_id}
Update a task.

**Request Body** (all fields optional)
```json
{
  "status": "completed",
  "assignee_id": "user_002"
}
```

**Response** `200 OK`
```json
{
  "message": "Task updated successfully"
}
```

---

## Agents 🤖

### POST /api/v1/projects/{project_id}/agents/analyze
Run ALL agents on the project.

**Response** `200 OK`
```json
{
  "planning": {
    "agent_name": "PlanningAgent",
    "status_summary": "Project planning is well-structured with clear milestones",
    "risks": [
      "Milestone 2 depends on unfinished Milestone 1 tasks"
    ],
    "recommendations": [
      {
        "action": "Complete blocking tasks before starting dependent work",
        "priority": "high",
        "reasoning": "Dependency chain shows 3 tasks blocked",
        "affected_entities": ["task_123", "task_456"]
      }
    ],
    "generated_at": "2024-01-20T10:30:00Z"
  },
  "coordination": { ... },
  "risk": { ... },
  "reporting": { ... }
}
```

---

### POST /api/v1/projects/{project_id}/agents/analyze/{agent_name}
Run a specific agent.

**Valid Agent Names**: `planning`, `coordination`, `risk`, `reporting`

**Response** `200 OK`
```json
{
  "agent_name": "RiskAgent",
  "status_summary": "2 medium risks detected",
  "risks": [
    "[MEDIUM] Task 'Unit tests' blocked for 3 days",
    "[LOW] CI/CD pipeline has no owner"
  ],
  "recommendations": [
    {
      "action": "Unblock unit testing by completing agent implementations",
      "priority": "medium",
      "reasoning": "Testing cannot proceed without code to test",
      "affected_entities": ["task_789"]
    }
  ],
  "generated_at": "2024-01-20T10:30:00Z"
}
```

---

### POST /api/v1/projects/{project_id}/agents/report
Generate comprehensive executive report.

**Response** `200 OK`
```json
{
  "report": "STATUS: Project on track with minor risks\n\nPROJECT SUMMARY:\nThe PM Agentic Workflow MVP is progressing well with 2 of 7 tasks completed...\n\nCOMPLETED THIS PERIOD:\n- Set up FastAPI project structure\n- Implement MongoDB integration\n\nIN PROGRESS:\n- Create Pydantic data models (user_002)\n- Implement Planning Agent (user_001)\n\nRISKS:\n- [MEDIUM] Agent testing blocked\n- [LOW] Unassigned DevOps task\n\nRECOMMENDED ACTION:\nPrioritize agent implementation to unblock testing."
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid project ID"
}
```

### 404 Not Found
```json
{
  "detail": "Project not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Agent analysis failed: <error details>"
}
```

---

## Event Types (Audit Trail)

Events are automatically logged for task changes:
- `task_created`
- `task_updated`
- `task_completed`
- `task_blocked`
- `risk_detected`
- `risk_resolved`
- `milestone_reached`
- `agent_action`

---

## Interactive Documentation

Access Swagger UI at: `http://localhost:8000/docs`

Access ReDoc at: `http://localhost:8000/redoc`

---

## Example: Full Workflow

```bash
# 1. Create a project
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "New Project", "owner_id": "user_001"}'

# Response: {"id": "abc123", "message": "Project created successfully"}

# 2. Add tasks
curl -X POST http://localhost:8000/api/v1/projects/abc123/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Setup backend", "status": "in_progress", "assignee_id": "user_001"}'

# 3. Run agent analysis
curl -X POST http://localhost:8000/api/v1/projects/abc123/agents/analyze

# 4. Get executive report
curl -X POST http://localhost:8000/api/v1/projects/abc123/agents/report
```

---

## Rate Limits

No rate limits currently implemented. Consider adding for production.

## Versioning

API is versioned via URL path (`/api/v1/`). Breaking changes will increment version.
