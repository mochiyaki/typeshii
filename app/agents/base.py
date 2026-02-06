"""
Base Agent Class - Foundation for all PM agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.llm import get_llm_client, LLMClient
from app.models import AgentOutput, AgentRecommendation


class BaseAgent(ABC):
    """Abstract base class for all PM workflow agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.llm: LLMClient = get_llm_client()
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Agent-specific system prompt."""
        pass
    
    @abstractmethod
    async def analyze(self, project_state: Dict[str, Any]) -> AgentOutput:
        """
        Analyze project state and return structured output.
        
        Args:
            project_state: Current project state including tasks, risks, milestones
            
        Returns:
            AgentOutput with status, risks, and recommendations
        """
        pass
    
    def _format_project_state(self, project_state: Dict[str, Any]) -> str:
        """Format project state as a structured prompt."""
        sections = []
        
        if "project" in project_state:
            p = project_state["project"]
            sections.append(f"PROJECT: {p.get('name', 'Unknown')}")
            sections.append(f"Target End Date: {p.get('target_end_date', 'Not set')}")
        
        if "tasks" in project_state:
            sections.append("\nTASKS:")
            for t in project_state["tasks"]:
                status = t.get("status", "unknown")
                due = t.get("due_date", "no due date")
                assignee = t.get("assignee_id", "unassigned")
                deps = ", ".join(t.get("dependencies", [])) or "none"
                sections.append(
                    f"  - [{status}] {t.get('title')} | Due: {due} | Assignee: {assignee} | Deps: {deps}"
                )
        
        if "milestones" in project_state:
            sections.append("\nMILESTONES:")
            for m in project_state["milestones"]:
                status = "✓" if m.get("is_completed") else "○"
                sections.append(f"  {status} {m.get('title')} | Target: {m.get('target_date', 'Not set')}")
        
        if "risks" in project_state:
            sections.append("\nACTIVE RISKS:")
            for r in project_state["risks"]:
                if not r.get("is_resolved"):
                    sections.append(f"  - [{r.get('level', 'unknown')}] {r.get('title')}")
        
        if "recent_events" in project_state:
            sections.append("\nRECENT EVENTS (last 24h):")
            for e in project_state["recent_events"][:10]:
                sections.append(f"  - {e.get('event_type')}: {e.get('entity_type')} | {e.get('details', {})}")
        
        return "\n".join(sections)
    
    def _parse_recommendations(self, raw_text: str) -> list[AgentRecommendation]:
        """Parse LLM output into structured recommendations."""
        recommendations = []
        
        # Simple parsing - look for action patterns
        lines = raw_text.split("\n")
        current_rec = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("ACTION:") or line.startswith("- ACTION:"):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = AgentRecommendation(
                    action=line.replace("ACTION:", "").replace("- ", "").strip(),
                    priority="medium",
                    reasoning="",
                    affected_entities=[],
                )
            elif current_rec:
                if line.startswith("PRIORITY:"):
                    priority = line.replace("PRIORITY:", "").strip().lower()
                    if priority in ["low", "medium", "high"]:
                        current_rec.priority = priority
                elif line.startswith("REASON:") or line.startswith("REASONING:"):
                    current_rec.reasoning = line.split(":", 1)[1].strip()
                elif line.startswith("AFFECTS:"):
                    entities = line.replace("AFFECTS:", "").strip()
                    current_rec.affected_entities = [e.strip() for e in entities.split(",")]
        
        if current_rec:
            recommendations.append(current_rec)
        
        return recommendations
