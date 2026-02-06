"""
Tasks API routes - CRUD operations for tasks.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import get_database
from app.models import TaskCreate, TaskUpdate, TaskStatus, EventType

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


async def log_event(
    db: AsyncIOMotorDatabase,
    project_id: str,
    event_type: EventType,
    entity_id: str,
    actor: str,
    details: dict,
):
    """Log an event to the audit trail."""
    event = {
        "project_id": project_id,
        "event_type": event_type.value,
        "entity_type": "task",
        "entity_id": entity_id,
        "actor": actor,
        "details": details,
        "timestamp": datetime.utcnow(),
    }
    await db.events.insert_one(event)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: str,
    task: TaskCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Create a new task in a project."""
    # Verify project exists
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_dict = task.model_dump()
    task_dict["project_id"] = project_id
    task_dict["created_at"] = datetime.utcnow()
    task_dict["updated_at"] = datetime.utcnow()
    
    result = await db.tasks.insert_one(task_dict)
    task_id = str(result.inserted_id)
    
    # Log event
    await log_event(
        db, project_id, EventType.TASK_CREATED, task_id, "system",
        {"title": task.title, "status": task.status.value},
    )
    
    return {"id": task_id, "message": "Task created successfully"}


@router.get("/", response_model=List[dict])
async def list_tasks(
    project_id: str,
    status_filter: Optional[TaskStatus] = None,
    assignee_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """List tasks in a project with optional filters."""
    query = {"project_id": project_id}
    if status_filter:
        query["status"] = status_filter.value
    if assignee_id:
        query["assignee_id"] = assignee_id
    
    cursor = db.tasks.find(query).skip(skip).limit(limit)
    tasks = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        tasks.append(doc)
    return tasks


@router.get("/{task_id}", response_model=dict)
async def get_task(
    project_id: str,
    task_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get a specific task."""
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = await db.tasks.find_one({
        "_id": ObjectId(task_id),
        "project_id": project_id,
    })
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task["_id"] = str(task["_id"])
    return task


@router.patch("/{task_id}", response_model=dict)
async def update_task(
    project_id: str,
    task_id: str,
    update: TaskUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Update a task."""
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    # Get current task for comparison
    current = await db.tasks.find_one({
        "_id": ObjectId(task_id),
        "project_id": project_id,
    })
    if not current:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
    if "status" in update_dict:
        update_dict["status"] = update_dict["status"].value
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_dict},
    )
    
    # Log appropriate event
    if update.status:
        if update.status == TaskStatus.COMPLETED:
            event_type = EventType.TASK_COMPLETED
        elif update.status == TaskStatus.BLOCKED:
            event_type = EventType.TASK_BLOCKED
        else:
            event_type = EventType.TASK_UPDATED
        
        await log_event(
            db, project_id, event_type, task_id, "system",
            {"old_status": current.get("status"), "new_status": update.status.value},
        )
    
    return {"message": "Task updated successfully"}


@router.delete("/{task_id}", response_model=dict)
async def delete_task(
    project_id: str,
    task_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Delete a task."""
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    result = await db.tasks.delete_one({
        "_id": ObjectId(task_id),
        "project_id": project_id,
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}
