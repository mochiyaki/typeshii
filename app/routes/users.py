"""
Users API routes - Simple user data for name resolution.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/users", tags=["users"])

# Mock users for MVP name resolution
MOCK_USERS = {
    "user_001": {"id": "user_001", "name": "Jay Tech", "role": "Full Stack Dev"},
    "user_002": {"id": "user_002", "name": "Sarah Chen", "role": "AI Engineer"},
    "user_003": {"id": "user_003", "name": "Alex Rivier", "role": "PM"},
    "manager_99": {"id": "manager_99", "name": "Manjesh Prasad", "role": "Senior Manager"},
    "dev_01": {"id": "dev_01", "name": "Liam Smith", "role": "Senior Dev"},
    "dev_02": {"id": "dev_02", "name": "Ava Johnson", "role": "Backend Dev"},
    "designer_01": {"id": "designer_01", "name": "Noah Miller", "role": "UX Designer"},
    "qa_01": {"id": "qa_01", "name": "Isabella Brown", "role": "QA Analyst"},
}

@router.get("/", response_model=List[dict])
async def list_users():
    """List all available users."""
    return list(MOCK_USERS.values())

@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: str):
    """Get a specific user by ID."""
    user = MOCK_USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
