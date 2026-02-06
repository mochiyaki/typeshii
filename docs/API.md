# PM Agentic Workflow - API Documentation

Complete API documentation for integrating with the PM Agentic Workflow backend.

## Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://typeshii-dl2b.onrender.com`

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
  "team_members": ["user_001", "user_002"]
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

### GET /api/v1/projects/?active_only=true
List all projects.

**Response** `ApiProject[]`

---

### GET /api/v1/projects/{id}/state
Get full project state (project + tasks + milestones + risks + events).
**Matches `ApiProjectState` on frontend.**

---

## Tasks

### GET /api/v1/projects/{projectId}/tasks/?limit=100&status_filter=pending
List tasks in a project.

---

### POST /api/v1/projects/{projectId}/tasks/
Create a task.

---

### PATCH /api/v1/projects/{projectId}/tasks/{taskId}
Update a task. (Use `{ status: "cancelled" }` for soft delete).

---

## Milestones 🏁

### POST /api/v1/projects/{id}/milestones/
Create a milestone.

---

### GET /api/v1/projects/{id}/milestones/
List milestones.

---

### PATCH /api/v1/projects/{id}/milestones/{milestone_id}
Update a milestone.

---

## AI Agents 🤖

### POST /api/v1/projects/{id}/agents/analyze
Run all agents and return `Record<string, ApiAgentOutput>`.

---

### POST /api/v1/projects/{id}/agents/split-ticket 🆕
**Dynamic Ticket Splitting**: Break down a topic into subtasks.

**Request Body**
```json
{
  "topic": "Implement user authentication",
  "context": "OAuth2 with Google and GitHub"
}
```

**Response**
```json
{
  "parent_task": { "title": "...", "description": "...", "priority": 2 },
  "subtasks": [
    { "title": "Subtask 1", "priority": 2, "labels": ["auth"] },
    ...
  ],
  "reasoning": "..."
}
```

---

### POST /api/v1/projects/{id}/agents/report
Generate a markdown executive report.
