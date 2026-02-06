"""
Seed script - Creates a realistic e-commerce project with tasks, milestones, and risks.
Run: python seed_realistic.py
"""
from pymongo import MongoClient
from datetime import datetime, timedelta, UTC
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("MONGODB_URI", "mongodb+srv://JayTech_456:%23Sunset123@agentic.prrlq6h.mongodb.net/typeshii?retryWrites=true&w=majority&appName=Agentic")

def seed_database():
    client = MongoClient(CONNECTION_STRING)
    db = client["typeshii"]
    
    # Optional: Clear everything for a clean demo
    # db.projects.delete_many({})
    # db.tasks.delete_many({})
    # db.milestones.delete_many({})
    # db.risks.delete_many({})
    # db.events.delete_many({})
    
    print("🚀 Seeding 3 massive realistic projects...")
    
    projects_to_seed = [
        {
            "id": str(ObjectId()),
            "name": "E-commerce Platform 2.0",
            "desc": "Modernizing core retail platform with headless CMS and AI.",
            "owner": "manager_99",
            "members": ["manager_99", "dev_01", "dev_02", "designer_01"],
            "days_ago": 30,
            "target_days": 60,
            "status": "In Progress"
        },
        {
            "id": str(ObjectId()),
            "name": "Mobile App Redesign",
            "desc": "Complete overhaul of the iOS/Android app to support new loyalty features.",
            "owner": "user_003",
            "members": ["user_003", "dev_01", "qa_01", "designer_02"],
            "days_ago": 10,
            "target_days": 20,
            "status": "At Risk"
        },
        {
            "id": str(ObjectId()),
            "name": "Cloud Migration Phase 2",
            "desc": "Moving legacy databases to distributed globally-available clusters.",
            "owner": "user_002",
            "members": ["user_002", "dev_02", "dev_01", "qa_01"],
            "days_ago": 5,
            "target_days": 90,
            "status": "Planning"
        }
    ]

    for p_info in projects_to_seed:
        p_id = p_info["id"]
        project = {
            "_id": ObjectId(p_id),
            "name": p_info["name"],
            "description": p_info["desc"],
            "owner_id": p_info["owner"],
            "team_members": p_info["members"],
            "start_date": datetime.now(UTC) - timedelta(days=p_info["days_ago"]),
            "target_end_date": datetime.now(UTC) + timedelta(days=p_info["target_days"]),
            "is_active": True,
            "created_at": datetime.now(UTC) - timedelta(days=p_info["days_ago"] + 5),
            "updated_at": datetime.now(UTC),
        }
        db.projects.insert_one(project)
        print(f"✅ Project: {p_info['name']}")

        # Seed Milestones for each
        m_ids = [str(ObjectId()) for _ in range(3)]
        milestones = []
        for i, m_id in enumerate(m_ids):
            is_done = i == 0 and p_info["days_ago"] > 15
            milestones.append({
                "_id": ObjectId(m_id),
                "project_id": p_id,
                "title": f"Phase {i+1}: {['Architecture', 'Implementation', 'Deployment'][i]}",
                "description": f"Focusing on the {['foundation', 'core features', 'final rollout'][i]} of {p_info['name']}.",
                "target_date": datetime.now(UTC) + timedelta(days=(i+1)*20),
                "is_completed": is_done,
                "created_at": datetime.now(UTC) - timedelta(days=p_info["days_ago"]),
                "updated_at": datetime.now(UTC),
                "completed_at": datetime.now(UTC) - timedelta(days=2) if is_done else None
            })
        db.milestones.insert_many(milestones)

        # Seed Tasks for each
        task_count = 8
        tasks = []
        for i in range(task_count):
            status = "completed" if i < 3 else ("in_progress" if i < 5 else "pending")
            if p_info["status"] == "At Risk" and i == 4: status = "blocked"
            
            t_id = ObjectId()
            tasks.append({
                "_id": t_id,
                "project_id": p_id,
                "milestone_id": m_ids[i // 3],
                "title": f"Dev Task {i+1}: {['Logic', 'UI', 'DB', 'API', 'Tests', 'Docs', 'Auth', 'CI'][i]}",
                "description": f"Work related to {['logic', 'ui', 'db', 'api', 'tests', 'docs', 'auth', 'ci'][i]} for {p_info['name']}.",
                "status": status,
                "assignee_id": p_info["members"][i % len(p_info["members"])],
                "priority": (i % 3) + 1,
                "due_date": datetime.now(UTC) + timedelta(days=(i-3)*5),
                "labels": [["backend", "frontend", "devops", "design"][i % 4]],
                "created_at": datetime.now(UTC) - timedelta(days=p_info["days_ago"]),
                "updated_at": datetime.now(UTC),
            })
        db.tasks.insert_many(tasks)

        # Seed 1 Risk per project
        risk = {
            "project_id": p_id,
            "title": f"Potential Delay in {p_info['name']}",
            "description": "Risk related to dependency bottlenecks or resource availability.",
            "level": "high" if p_info["status"] == "At Risk" else "low",
            "mitigation": "Increase team bandwidth or adjust scope.",
            "is_resolved": False,
            "detected_by": "system",
            "created_at": datetime.now(UTC) - timedelta(days=2),
            "updated_at": datetime.now(UTC),
        }
        db.risks.insert_one(risk)

    print(f"\n🎉 3 massive projects seeded successfully!")
    client.close()

if __name__ == "__main__":
    seed_database()
