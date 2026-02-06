from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    """Risk severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(str, Enum):
    """Project event types for audit trail."""
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_BLOCKED = "task_blocked"
    RISK_DETECTED = "risk_detected"
    RISK_RESOLVED = "risk_resolved"
    MILESTONE_REACHED = "milestone_reached"
    AGENT_ACTION = "agent_action"
    COMMENT_ADDED = "comment_added"


# --- Base Models ---

class TimestampMixin(BaseModel):
    """Mixin for created/updated timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --- Task Model ---

class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    assignee_id: Optional[str] = None
    priority: int = Field(default=2, ge=1, le=5)  # 1=highest, 5=lowest
    due_date: Optional[datetime] = None
    dependencies: List[str] = Field(default_factory=list)  # List of task IDs
    labels: List[str] = Field(default_factory=list)


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    milestone_id: Optional[str] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[datetime] = None
    dependencies: Optional[List[str]] = None
    labels: Optional[List[str]] = None


class TaskInDB(TaskBase, TimestampMixin):
    """Task as stored in database."""
    id: str = Field(alias="_id")
    project_id: str
    milestone_id: Optional[str] = None
    
    class Config:
        populate_by_name = True


# --- Risk Model ---

class RiskBase(BaseModel):
    """Base risk schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    level: RiskLevel = RiskLevel.MEDIUM
    affected_tasks: List[str] = Field(default_factory=list)
    mitigation: Optional[str] = None
    is_resolved: bool = False


class RiskCreate(RiskBase):
    """Schema for creating a risk."""
    pass


class RiskInDB(RiskBase, TimestampMixin):
    """Risk as stored in database."""
    id: str = Field(alias="_id")
    project_id: str
    detected_by: str = "system"  # "system" or agent name
    resolved_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


# --- Milestone Model ---

class MilestoneBase(BaseModel):
    """Base milestone schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    is_completed: bool = False


class MilestoneCreate(MilestoneBase):
    """Schema for creating a milestone."""
    pass


class MilestoneInDB(MilestoneBase, TimestampMixin):
    """Milestone as stored in database."""
    id: str = Field(alias="_id")
    project_id: str
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


# --- Event Model (Audit Trail) ---

class EventBase(BaseModel):
    """Base event schema for audit trail."""
    event_type: EventType
    entity_type: str  # "task", "risk", "milestone", "project"
    entity_id: str
    actor: str  # user ID or agent name
    details: dict = Field(default_factory=dict)


class EventCreate(EventBase):
    """Schema for creating an event."""
    pass


class EventInDB(EventBase):
    """Event as stored in database."""
    id: str = Field(alias="_id")
    project_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# --- Project Model ---

class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    owner_id: str
    team_members: List[str] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    target_end_date: Optional[datetime] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    team_members: Optional[List[str]] = None
    target_end_date: Optional[datetime] = None


class ProjectInDB(ProjectBase, TimestampMixin):
    """Project as stored in database."""
    id: str = Field(alias="_id")
    is_active: bool = True
    
    class Config:
        populate_by_name = True


# --- Agent Output Models ---

class AgentRecommendation(BaseModel):
    """Structured recommendation from an agent for the UI."""
    title: str
    priority: str  # "low", "medium", "high", "critical"
    category: str  # "planning", "coordination", "risk", "performance"
    suggestion: str  # What the user should actually do
    reasoning: str  # Detailed impact/background
    affected_entities: List[str] = Field(default_factory=list)


class AgentOutput(BaseModel):
    """Standard output format for all agents."""
    agent_name: str
    status_summary: str
    risks: List[str] = Field(default_factory=list)
    recommendations: List[AgentRecommendation] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
