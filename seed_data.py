"""
Seed script - Creates sample project with tasks, milestones, and risks.
Run: python seed_data.py
"""
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId

CONNECTION_STRING = "mongodb+srv://JayTech_456:%23Sunset123@agentic.prrlq6h.mongodb.net/typeshii?retryWrites=true&w=majority&appName=Agentic"

def seed_database():
    client = MongoClient(CONNECTION_STRING)
    db = client["typeshii"]
    
    # Clear existing data
    db.projects.delete_many({})
    db.tasks.delete_many({})
    db.milestones.delete_many({})
    db.risks.delete_many({})
    db.events.delete_many({})
    
    print("🧹 Cleared existing data")
    
    # Create sample project
    project_id = str(ObjectId())
    project = {
        "_id": ObjectId(project_id),
        "name": "PM Agentic Workflow MVP",
        "description": "Build an AI-powered project management system with autonomous agents",
        "owner_id": "user_001",
        "team_members": ["user_001", "user_002", "user_003"],
        "start_date": datetime.utcnow() - timedelta(days=14),
        "target_end_date": datetime.utcnow() + timedelta(days=30),
        "is_active": True,
        "created_at": datetime.utcnow() - timedelta(days=14),
        "updated_at": datetime.utcnow(),
    }
    db.projects.insert_one(project)
    print(f"✅ Created project: {project['name']} (ID: {project_id})")
    
    # Create milestones
    milestone_1_id = str(ObjectId())
    milestone_2_id = str(ObjectId())
    milestones = [
        {
            "_id": ObjectId(milestone_1_id),
            "project_id": project_id,
            "title": "Backend API Complete",
            "description": "All API endpoints implemented and tested",
            "target_date": datetime.utcnow() + timedelta(days=7),
            "is_completed": False,
            "created_at": datetime.utcnow() - timedelta(days=14),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(milestone_2_id),
            "project_id": project_id,
            "title": "Agent Integration Complete",
            "description": "All 4 agents integrated with LLM and tested",
            "target_date": datetime.utcnow() + timedelta(days=21),
            "is_completed": False,
            "created_at": datetime.utcnow() - timedelta(days=14),
            "updated_at": datetime.utcnow(),
        },
    ]
    db.milestones.insert_many(milestones)
    print(f"✅ Created {len(milestones)} milestones")
    
    # Create tasks
    tasks = [
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "milestone_id": milestone_1_id,
            "title": "Set up FastAPI project structure",
            "description": "Initialize project with FastAPI, configure routes",
            "status": "completed",
            "assignee_id": "user_001",
            "priority": 1,
            "due_date": datetime.utcnow() - timedelta(days=7),
            "dependencies": [],
            "labels": ["backend", "setup"],
            "created_at": datetime.utcnow() - timedelta(days=14),
            "updated_at": datetime.utcnow() - timedelta(days=7),
        },
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "milestone_id": milestone_1_id,
            "title": "Implement MongoDB integration",
            "description": "Set up async MongoDB connection with Motor",
            "status": "completed",
            "assignee_id": "user_001",
            "priority": 1,
            "due_date": datetime.utcnow() - timedelta(days=5),
            "dependencies": [],
            "labels": ["backend", "database"],
            "created_at": datetime.utcnow() - timedelta(days=12),
            "updated_at": datetime.utcnow() - timedelta(days=5),
        },
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "milestone_id": milestone_1_id,
            "title": "Create Pydantic data models",
            "description": "Define schemas for projects, tasks, risks, events",
            "status": "in_progress",
            "assignee_id": "user_002",
            "priority": 2,
            "due_date": datetime.utcnow() + timedelta(days=2),
            "dependencies": [],
            "labels": ["backend", "models"],
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "milestone_id": milestone_2_id,
            "title": "Implement Planning Agent",
            "description": "Create agent that analyzes project structure and dependencies",
            "status": "in_progress",
            "assignee_id": "user_001",
            "priority": 1,
            "due_date": datetime.utcnow() + timedelta(days=5),
            "dependencies": [],
            "labels": ["agents", "ai"],
            "created_at": datetime.utcnow() - timedelta(days=7),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "milestone_id": milestone_2_id,
            "title": "Implement Risk Agent",
            "description": "Create agent that detects delivery risks",
            "status": "pending",
            "assignee_id": "user_002",
            "priority": 2,
            "due_date": datetime.utcnow() + timedelta(days=10),
            "dependencies": [],
            "labels": ["agents", "ai"],
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "milestone_id": milestone_2_id,
            "title": "Write unit tests for agents",
            "description": "Create comprehensive test suite for all agents",
            "status": "blocked",
            "assignee_id": "user_003",
            "priority": 3,
            "due_date": datetime.utcnow() + timedelta(days=14),
            "dependencies": [],
            "labels": ["testing", "agents"],
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "milestone_id": None,
            "title": "Set up CI/CD pipeline",
            "description": "Configure GitHub Actions for automated testing and deployment",
            "status": "pending",
            "assignee_id": None,
            "priority": 4,
            "due_date": datetime.utcnow() + timedelta(days=20),
            "dependencies": [],
            "labels": ["devops"],
            "created_at": datetime.utcnow() - timedelta(days=2),
            "updated_at": datetime.utcnow(),
        },
    ]
    db.tasks.insert_many(tasks)
    print(f"✅ Created {len(tasks)} tasks")
    
    # Create risks
    risks = [
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "title": "Agent testing blocked",
            "description": "Unit tests cannot proceed until agents are complete",
            "level": "medium",
            "affected_tasks": [],
            "mitigation": "Prioritize agent implementation",
            "is_resolved": False,
            "detected_by": "system",
            "created_at": datetime.utcnow() - timedelta(days=1),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "title": "Unassigned DevOps task",
            "description": "CI/CD pipeline setup has no owner",
            "level": "low",
            "affected_tasks": [],
            "mitigation": "Assign to available team member",
            "is_resolved": False,
            "detected_by": "system",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ]
    db.risks.insert_many(risks)
    print(f"✅ Created {len(risks)} risks")
    
    # Create events
    events = [
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "event_type": "task_completed",
            "entity_type": "task",
            "entity_id": str(tasks[0]["_id"]),
            "actor": "user_001",
            "details": {"title": "Set up FastAPI project structure"},
            "timestamp": datetime.utcnow() - timedelta(days=7),
        },
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "event_type": "task_completed",
            "entity_type": "task",
            "entity_id": str(tasks[1]["_id"]),
            "actor": "user_001",
            "details": {"title": "Implement MongoDB integration"},
            "timestamp": datetime.utcnow() - timedelta(days=5),
        },
        {
            "_id": ObjectId(),
            "project_id": project_id,
            "event_type": "risk_detected",
            "entity_type": "risk",
            "entity_id": str(risks[0]["_id"]),
            "actor": "system",
            "details": {"title": "Agent testing blocked", "level": "medium"},
            "timestamp": datetime.utcnow() - timedelta(days=1),
        },
    ]
    db.events.insert_many(events)
    print(f"✅ Created {len(events)} events")
    
    print(f"\n🎉 Database seeded successfully!")
    print(f"\n📌 Project ID: {project_id}")
    print(f"Use this ID to test the API endpoints")
    
    client.close()

if __name__ == "__main__":
    seed_database()
