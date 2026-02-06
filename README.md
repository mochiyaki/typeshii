# PM Agentic Workflow Backend

AI-powered project management coordination system built with FastAPI, MongoDB, and Grok (xAI).

Demo link (hosted on lovable): https://pulse-project-assist.lovable.app/

## Overview

This backend provides an autonomous PM coordination layer that uses 4 specialized AI agents to:
- Analyze project planning and dependencies
- Track task progress and detect stalled work
- Monitor delivery risks
- Generate stakeholder reports

**Core Principle**: The system owns delivery awareness and process optimization, NOT implementation or content decisions.

## System Architecture

### High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        PM Agentic Workflow System                        │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │   Frontend  │  │   API Layer │   │   Agents    │   │   Data Layer│    │
│  │             │  │             │   │             │   │             │    │
│  │  Web App    │─▶│  FastAPI   │──▶│  Planning   │─▶│  MongoDB    │    │
│  │  Mobile     │  │  Routes     │   │ Coordination│   │  (Motor)    │    │
│  │  Dashboard  │  │             │   │  Risk       │   │             │    │
│  └─────────────┘  │             │   │  Reporting  │   │             │    │
│                   │             │   │             │   │             │    │
│                   │             │   │             │   │             │    │
│                   │             │   │             │   │             │    │
│                   └─────────────┘   └─────────────┘   └─────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
```

### Agent Workflow

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                 Agent Orchestration                                                           │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Project State → [All Agents Run in Parallel] → [Reporting Agent Aggregates Insights] → [Return Consolidated Output]          │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐  │
│  │  Planning   │   │ Coordination│   │    Risk     │   │  Reporting  │   │ Orchestrator│   │  Data Layer │   │  LLM API    │  │
│  │   Agent     │   │   Agent     │   │   Agent     │   │   Agent     │   │             │   │             │   │             │  │
│  │             │   │             │   │             │   │             │   │             │   │             │   │             │  │
│  │  Analyzes   │   │  Tracks     │   │  Monitors   │   │  Aggregates │   │  Coordinates│   │  Project    │   │  Grok       │  │
│  │  Milestones │   │  Task       │   │  Delivery   │   │  Insights   │   │  All Agents │   │  State      │   │  Client     │  │
│  │ Dependencies│   │  Progress   │   │  Risks      │   │  into       │   │             │   │             │   │             │  │
│  │  Sequencing │   │  Stalls     │   │             │   │  Executive  │   │             │   │             │   │             │  │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
app/
├── main.py                 # FastAPI app entry point
├── core/
│   ├── config.py          # Environment settings
│   ├── database.py        # MongoDB async connection
│   └── llm.py             # Grok API client
├── models/
│   └── schemas.py         # Pydantic data models
├── agents/
│   ├── base.py            # Abstract base agent
│   ├── planning.py        # Planning Agent
│   ├── coordination.py    # Coordination Agent
│   ├── risk.py            # Risk Agent
│   ├── reporting.py       # Reporting Agent
│   ├── orchestrator.py    # Agent coordinator
│   └── ticket_splitter.py # Ticket splitting agent
└── routes/
    ├── projects.py        # Project endpoints
    ├── tasks.py           # Task endpoints
    └── agents.py          # Agent trigger endpoints
```

## Quick Start

### Prerequisites
- Python 3.10+
- MongoDB Atlas account
- Grok API key from [x.ai](https://x.ai)

### Setup

```bash
# Clone and navigate
cd /path/to/Typeshii

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Seed sample data (optional)
python seed_data.py

# Run server
uvicorn app.main:app --reload --port 8000
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/db` |
| `GROK_API_KEY` | Grok API key | `xai-...` |
| `GROK_MODEL` | Grok model name | `grok-4-1-fast-reasoning` |
| `ENVIRONMENT` | Environment mode | `development` or `production` |
| `LOG_LEVEL` | Logging level | `debug`, `info`, `warning` |

## API Reference

Base URL: `http://localhost:8000/api/v1`

### Health Check
```
GET /health
Response: { "status": "healthy", "version": "1.0.0", "database": "connected" }
```

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/projects/` | Create project |
| GET | `/projects/` | List projects |
| GET | `/projects/{id}` | Get project |
| PATCH | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Soft delete project |
| GET | `/projects/{id}/state` | Get full project state (for agents) |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/projects/{id}/tasks/` | Create task |
| GET | `/projects/{id}/tasks/` | List tasks (with filters) |
| GET | `/projects/{id}/tasks/{task_id}` | Get task |
| PATCH | `/projects/{id}/tasks/{task_id}` | Update task |
| DELETE | `/projects/{id}/tasks/{task_id}` | Delete task |

### Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/projects/{id}/agents/analyze` | Run ALL agents |
| POST | `/projects/{id}/agents/analyze/{agent}` | Run specific agent |
| POST | `/projects/{id}/agents/report` | Generate executive report |
| POST | `/projects/{id}/agents/split-ticket` | Split topic into subtasks |

Valid agent names: `planning`, `coordination`, `risk`, `reporting`

## Data Models

### Project
```json
{
  "name": "string",
  "description": "string",
  "owner_id": "string",
  "team_members": ["user_id"],
  "start_date": "ISO datetime",
  "target_end_date": "ISO datetime",
  "is_active": true
}
```

### Task
```json
{
  "title": "string",
  "description": "string",
  "status": "pending|in_progress|blocked|in_review|completed|cancelled",
  "assignee_id": "string",
  "priority": 1-5,
  "due_date": "ISO datetime",
  "dependencies": ["task_id"],
  "labels": ["string"],
  "milestone_id": "string"
}
```

### Risk
```json
{
  "title": "string",
  "description": "string",
  "level": "low|medium|high|critical",
  "affected_tasks": ["task_id"],
  "mitigation": "string",
  "is_resolved": false
}
```

### Agent Output
```json
{
  "agent_name": "PlanningAgent",
  "status_summary": "string",
  "risks": ["risk description"],
  "recommendations": [
    {
      "title": "string",
      "priority": "low|medium|high|critical",
      "category": "string",
      "suggestion": "string",
      "reasoning": "string",
      "affected_entities": ["id"]
    }
  ],
  "generated_at": "ISO datetime"
}
```

## Agent Behaviors

### Planning Agent
- Evaluates milestone sequencing
- Identifies missing dependencies
- Flags unrealistic timelines
- Does NOT define implementation details

### Coordination Agent
- Tracks task progress
- Detects stalled work (in_progress too long)
- Identifies missing handoffs
- Suggests communication actions

### Risk Agent
- Monitors blocked tasks
- Detects overdue work
- Identifies dependency failures
- Assigns risk levels with evidence

### Reporting Agent
- Generates stakeholder summaries
- Aggregates insights from other agents
- Focuses on status, risks, next actions

## Deployment

### Docker
```bash
docker build -t typeshii-backend .
docker run -p 8000:8000 \
  -e MONGODB_URI="your-uri" \
  -e GROK_API_KEY="your-key" \
  typeshii-backend
```

### Render
1. Push to GitHub
2. Create Web Service on Render
3. Connect repository
4. Set environment variables
5. Deploy (uses `render.yaml`)

## Frontend Integration

### CORS
CORS is enabled for all origins in development. Configure appropriately for production.

### Authentication
Currently no authentication. Add JWT/OAuth as needed for production.

### WebSocket (Future)
Consider adding WebSocket for real-time agent updates.

## License
MIT
