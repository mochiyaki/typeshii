"""
Projects API routes - CRUD operations for projects.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import get_database
from app.models import ProjectCreate, ProjectUpdate, ProjectInDB, EventCreate, EventType

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Create a new project."""
    project_dict = project.model_dump()
    project_dict["created_at"] = datetime.utcnow()
    project_dict["updated_at"] = datetime.utcnow()
    project_dict["is_active"] = True
    
    result = await db.projects.insert_one(project_dict)
    
    return {"id": str(result.inserted_id), "message": "Project created successfully"}


@router.get("/", response_model=List[dict])
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    active_only: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """List all projects with pagination."""
    query = {"is_active": True} if active_only else {}
    cursor = db.projects.find(query).skip(skip).limit(limit)
    projects = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        projects.append(doc)
    return projects


@router.get("/{project_id}", response_model=dict)
async def get_project(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get a specific project by ID."""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project["_id"] = str(project["_id"])
    return project


@router.patch("/{project_id}", response_model=dict)
async def update_project(
    project_id: str,
    update: ProjectUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Update a project."""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": update_dict},
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project updated successfully"}


@router.delete("/{project_id}", response_model=dict)
async def delete_project(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Soft delete a project (set is_active to False)."""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    result = await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}},
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/state", response_model=dict)
async def get_project_state(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get full project state including tasks, milestones, risks, and recent events.
    Matches ApiProjectState on frontend.
    """
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project["_id"] = str(project["_id"])
    
    # Fetch related entities
    tasks = []
    async for doc in db.tasks.find({"project_id": project_id}):
        doc["_id"] = str(doc["_id"])
        tasks.append(doc)
    
    milestones = []
    async for doc in db.milestones.find({"project_id": project_id}):
        doc["_id"] = str(doc["_id"])
        milestones.append(doc)
    
    risks = []
    async for doc in db.risks.find({"project_id": project_id}):
        doc["_id"] = str(doc["_id"])
        risks.append(doc)
    
    # Get recent events
    from datetime import timedelta
    # Use last 7 days of events as "recent" for the UI feed
    recent_cutoff = datetime.utcnow() - timedelta(days=7)
    recent_events = []
    async for doc in db.events.find({
        "project_id": project_id,
        "timestamp": {"$gte": recent_cutoff},
    }).sort("timestamp", -1).limit(100):
        doc["_id"] = str(doc["_id"])
        recent_events.append(doc)
    
    return {
        "project": project,
        "tasks": tasks,
        "milestones": milestones,
        "risks": risks,
        "recent_events": recent_events,
    }
