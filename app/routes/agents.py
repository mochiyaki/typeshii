"""
Agents API routes - Trigger agent analysis.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import get_database
from app.agents import get_orchestrator, AgentOrchestrator

router = APIRouter(prefix="/projects/{project_id}/agents", tags=["agents"])


async def get_project_state(project_id: str, db: AsyncIOMotorDatabase) -> dict:
    """Helper to fetch full project state for agents."""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project["_id"] = str(project["_id"])
    
    tasks = []
    async for doc in db.tasks.find({"project_id": project_id}):
        doc["_id"] = str(doc["_id"])
        tasks.append(doc)
    
    milestones = []
    async for doc in db.milestones.find({"project_id": project_id}):
        doc["_id"] = str(doc["_id"])
        milestones.append(doc)
    
    risks = []
    async for doc in db.risks.find({"project_id": project_id, "is_resolved": False}):
        doc["_id"] = str(doc["_id"])
        risks.append(doc)
    
    from datetime import datetime
    yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0)
    recent_events = []
    async for doc in db.events.find({
        "project_id": project_id,
        "timestamp": {"$gte": yesterday},
    }).sort("timestamp", -1).limit(50):
        doc["_id"] = str(doc["_id"])
        recent_events.append(doc)
    
    return {
        "project": project,
        "tasks": tasks,
        "milestones": milestones,
        "risks": risks,
        "recent_events": recent_events,
    }


@router.post("/analyze", response_model=dict)
async def run_full_analysis(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """
    Run all agents on the project and return comprehensive analysis.
    
    Returns:
        Dict with outputs from all agents (planning, coordination, risk, reporting)
    """
    project_state = await get_project_state(project_id, db)
    
    try:
        results = await orchestrator.run_full_analysis(project_state)
        
        # Convert to serializable format
        return {
            agent_name: {
                "agent_name": output.agent_name,
                "status_summary": output.status_summary,
                "risks": output.risks,
                "recommendations": [
                    {
                        "action": rec.action,
                        "priority": rec.priority,
                        "reasoning": rec.reasoning,
                        "affected_entities": rec.affected_entities,
                    }
                    for rec in output.recommendations
                ],
                "generated_at": output.generated_at.isoformat(),
            }
            for agent_name, output in results.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent analysis failed: {str(e)}")


@router.post("/analyze/{agent_name}", response_model=dict)
async def run_single_agent(
    project_id: str,
    agent_name: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """
    Run a specific agent on the project.
    
    Valid agent names: planning, coordination, risk, reporting
    """
    valid_agents = ["planning", "coordination", "risk", "reporting"]
    if agent_name.lower() not in valid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent name. Must be one of: {valid_agents}",
        )
    
    project_state = await get_project_state(project_id, db)
    
    try:
        output = await orchestrator.run_single_agent(agent_name, project_state)
        
        return {
            "agent_name": output.agent_name,
            "status_summary": output.status_summary,
            "risks": output.risks,
            "recommendations": [
                {
                    "action": rec.action,
                    "priority": rec.priority,
                    "reasoning": rec.reasoning,
                    "affected_entities": rec.affected_entities,
                }
                for rec in output.recommendations
            ],
            "generated_at": output.generated_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent analysis failed: {str(e)}")


@router.post("/report", response_model=dict)
async def generate_executive_report(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """
    Generate a comprehensive executive report using all agents.
    
    This runs all agents and produces a formatted stakeholder summary.
    """
    project_state = await get_project_state(project_id, db)
    
    try:
        report = await orchestrator.generate_executive_report(project_state)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
