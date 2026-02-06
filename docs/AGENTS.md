# PM Agentic Workflow - Agent System Documentation

This document explains how the AI agent system works for developers integrating with or extending the PM Agentic Workflow.

## Agent Philosophy

The agents follow a strict **coordination-only** principle:

> **Agents own visibility and coordination, NOT execution.**
> 
> They surface problems, propose solutions, but never make irreversible changes without human approval.

### What Agents DO:
- Analyze project state
- Detect risks and blockers
- Suggest actions
- Generate reports

### What Agents DO NOT:
- Modify task descriptions
- Change project requirements
- Edit code or documentation
- Make product/architectural decisions
- Simulate authority over human roles

---

## Agent Types

### 1. Planning Agent

**Purpose**: Converts goals into milestones and identifies sequencing risks.

**Analyzes**:
- Milestone sequencing
- Task dependencies
- Orphan tasks (no milestone)
- Timeline realism

**Example Output**:
```
STATUS: Planning structure needs attention

RISKS:
- Milestone 2 has tasks that depend on incomplete Milestone 1 tasks
- 2 tasks have no assigned milestone

RECOMMENDATIONS:
ACTION: Assign orphan tasks to appropriate milestones
PRIORITY: medium
REASON: Untracked tasks reduce delivery visibility
AFFECTS: task_abc, task_def
```

---

### 2. Coordination Agent

**Purpose**: Tracks task progress and detects stalled work.

**Analyzes**:
- Tasks stuck in `in_progress` too long
- Completed tasks with unstarted dependents
- Unassigned tasks
- Blocked tasks without documented blockers

**Example Output**:
```
STATUS: 1 stalled task detected

RISKS:
- Task "Implement Risk Agent" has been in_progress for 5 days without updates

RECOMMENDATIONS:
ACTION: Check in with user_002 on Risk Agent progress
PRIORITY: high
REASON: Extended in_progress status may indicate blockers
AFFECTS: user_002, task_risk_agent
```

---

### 3. Risk Agent

**Purpose**: Monitors delivery risk based on observable signals.

**Risk Levels**:
| Level | Description |
|-------|-------------|
| LOW | Minor impact, easily addressed |
| MEDIUM | Moderate impact, needs attention |
| HIGH | Significant impact, urgent action |
| CRITICAL | Severe impact, immediate intervention |

**Monitors**:
- Overdue tasks (past due_date)
- Blocked tasks
- Dependency failures
- Velocity trends
- Review bottlenecks

**Example Output**:
```
STATUS: 2 delivery risks detected

RISKS:
- [HIGH] 3 tasks are past their due dates
- [MEDIUM] Testing is blocked on agent completion

RECOMMENDATIONS:
ACTION: Reprioritize overdue tasks or adjust deadlines
PRIORITY: high
REASON: Overdue tasks: API endpoints (2d), Database schema (1d)
AFFECTS: task_api, task_schema
```

---

### 4. Reporting Agent

**Purpose**: Generates stakeholder summaries.

**Output Format**:
```
STATUS: [Overall health in one line]

PROJECT SUMMARY:
[2-3 sentences on current state]

COMPLETED THIS PERIOD:
- [Item 1]
- [Item 2]

IN PROGRESS:
- [Item with assignee]

RISKS:
- [Risk with severity]

RECOMMENDED ACTION:
[Next step]
```

---

## Agent Orchestration

The `AgentOrchestrator` coordinates all agents:

```python
from app.agents import get_orchestrator

orchestrator = get_orchestrator()

# Run all agents in parallel
results = await orchestrator.run_full_analysis(project_state)

# Run single agent
output = await orchestrator.run_single_agent("risk", project_state)

# Generate executive report (runs all agents first)
report = await orchestrator.generate_executive_report(project_state)
```

### Parallel Execution

Analysis agents (Planning, Coordination, Risk) run in parallel using `asyncio.gather()` for performance. Reporting runs last to aggregate their insights.

---

## Project State Format

Agents receive project state in this format:

```python
project_state = {
    "project": {
        "_id": "project_id",
        "name": "Project Name",
        "target_end_date": "2024-03-15T00:00:00Z",
        ...
    },
    "tasks": [
        {
            "_id": "task_id",
            "title": "Task title",
            "status": "in_progress",
            "assignee_id": "user_001",
            "due_date": "2024-02-01T00:00:00Z",
            "dependencies": ["other_task_id"],
            ...
        }
    ],
    "milestones": [
        {
            "_id": "milestone_id",
            "title": "Milestone 1",
            "target_date": "2024-02-15T00:00:00Z",
            "is_completed": false,
            ...
        }
    ],
    "risks": [
        {
            "_id": "risk_id",
            "title": "Risk title",
            "level": "medium",
            "is_resolved": false,
            ...
        }
    ],
    "recent_events": [
        {
            "event_type": "task_completed",
            "entity_type": "task",
            "entity_id": "task_id",
            "actor": "user_001",
            "details": {...},
            "timestamp": "2024-01-20T10:00:00Z"
        }
    ],
    "current_date": "2024-01-22T10:00:00Z"
}
```

---

## LLM Integration

Agents use Grok (xAI) via the `LLMClient`:

```python
from app.core.llm import get_llm_client

llm = get_llm_client()

# Simple chat
response = await llm.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.7
)

# Structured output (for agents)
response = await llm.structured_output(
    prompt="Analyze this project...",
    system_prompt="You are the Planning Agent...",
    temperature=0.3  # Lower for consistency
)
```

---

## Creating Custom Agents

To add a new agent:

1. Create `app/agents/my_agent.py`:

```python
from app.agents.base import BaseAgent
from app.models import AgentOutput

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyAgent")
    
    @property
    def system_prompt(self) -> str:
        return """You are MyAgent. Your responsibility is...
        
        Output format:
        STATUS: [summary]
        RISKS:
        - [risk]
        RECOMMENDATIONS:
        ACTION: [action]
        PRIORITY: [low/medium/high]
        REASON: [why]
        AFFECTS: [entities]"""
    
    async def analyze(self, project_state: dict) -> AgentOutput:
        prompt = f"Analyze: {self._format_project_state(project_state)}"
        
        response = await self.llm.structured_output(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.3
        )
        
        # Parse response...
        return AgentOutput(
            agent_name=self.name,
            status_summary="...",
            risks=[...],
            recommendations=[...]
        )
```

2. Add to `app/agents/__init__.py`
3. Register in `AgentOrchestrator` if needed

---

## Best Practices

### For Agent Prompts
- Be explicit about what agents should NOT do
- Use structured output formats
- Keep temperature low (0.3) for consistency
- Include current date for temporal reasoning

### For Project State
- Include recent events for velocity tracking
- Filter resolved risks
- Limit events to relevant timeframe

### For Error Handling
- Agents should degrade gracefully
- Log errors but return partial results
- Never crash the entire analysis

---

## Testing Agents

```python
# Create mock project state
project_state = {
    "project": {"name": "Test", ...},
    "tasks": [...],
    ...
}

# Test individual agent
from app.agents import PlanningAgent

agent = PlanningAgent()
output = await agent.analyze(project_state)

assert output.agent_name == "PlanningAgent"
assert isinstance(output.risks, list)
```
