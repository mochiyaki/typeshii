"""
Milestones API routes - CRUD operations for milestones.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import get_database
from app.models import MilestoneCreate, MilestoneInDB

router = APIRouter(prefix="/projects/{project_id}/milestones", tags=["milestones"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    project_id: str,
    milestone: MilestoneCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Create a new milestone."""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    milestone_dict = milestone.model_dump()
    milestone_dict["project_id"] = project_id
    milestone_dict["created_at"] = datetime.utcnow()
    milestone_dict["updated_at"] = datetime.utcnow()
    
    result = await db.milestones.insert_one(milestone_dict)
    
    return {"id": str(result.inserted_id), "message": "Milestone created successfully"}


@router.get("/", response_model=List[dict])
async def list_milestones(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """List all milestones for a project."""
    cursor = db.milestones.find({"project_id": project_id})
    milestones = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        milestones.append(doc)
    return milestones


@router.patch("/{milestone_id}", response_model=dict)
async def update_milestone(
    project_id: str,
    milestone_id: str,
    update: dict,  # Partial update
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Update a milestone."""
    if not ObjectId.is_valid(milestone_id):
        raise HTTPException(status_code=400, detail="Invalid milestone ID")
    
    update["updated_at"] = datetime.utcnow()
    if "is_completed" in update and update["is_completed"]:
        update["completed_at"] = datetime.utcnow()
    
    result = await db.milestones.update_one(
        {"_id": ObjectId(milestone_id), "project_id": project_id},
        {"$set": update},
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    return {"message": "Milestone updated successfully"}


@router.delete("/{milestone_id}", response_model=dict)
async def delete_milestone(
    project_id: str,
    milestone_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Delete a milestone."""
    if not ObjectId.is_valid(milestone_id):
        raise HTTPException(status_code=400, detail="Invalid milestone ID")
    
    result = await db.milestones.delete_one({
        "_id": ObjectId(milestone_id),
        "project_id": project_id,
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    return {"message": "Milestone deleted successfully"}
