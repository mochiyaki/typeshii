"""
Agent Orchestrator - Coordinates all agents for comprehensive project analysis.
"""
from typing import Dict, Any, List
from datetime import datetime

from app.agents.planning import PlanningAgent
from app.agents.coordination import CoordinationAgent
from app.agents.risk import RiskAgent
from app.agents.reporting import ReportingAgent
from app.models import AgentOutput


class AgentOrchestrator:
    """
    Orchestrates all PM agents for comprehensive analysis.
    Runs agents in parallel where possible for scalability.
    """
    
    def __init__(self):
        self.planning_agent = PlanningAgent()
        self.coordination_agent = CoordinationAgent()
        self.risk_agent = RiskAgent()
        self.reporting_agent = ReportingAgent()
    
    async def run_full_analysis(self, project_state: Dict[str, Any]) -> Dict[str, AgentOutput]:
        """
        Run all agents and return comprehensive analysis.
        
        Args:
            project_state: Current project state from database
            
        Returns:
            Dict mapping agent names to their outputs
        """
        # Add current date to project state
        project_state["current_date"] = datetime.utcnow().isoformat()
        
        # Run analysis agents (could be parallelized with asyncio.gather for scale)
        import asyncio
        
        planning_output, coordination_output, risk_output = await asyncio.gather(
            self.planning_agent.analyze(project_state),
            self.coordination_agent.analyze(project_state),
            self.risk_agent.analyze(project_state),
        )
        
        # Consolidation for the dashboard's "AI Insights" panel
        all_recs = (
            planning_output.recommendations + 
            coordination_output.recommendations + 
            risk_output.recommendations
        )
        
        # Prioritization: critical -> high -> medium -> low
        priority_map = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_recs.sort(key=lambda x: priority_map.get(x.priority.lower(), 10))
        
        # Reporting agent runs after to include other agents' insights
        reporting_output = await self.reporting_agent.analyze(project_state)
        
        return {
            "planning": planning_output,
            "coordination": coordination_output,
            "risk": risk_output,
            "reporting": reporting_output,
            "insights": all_recs  # Flat list of prioritized insights for the dashboard
        }
    
    async def run_single_agent(
        self,
        agent_name: str,
        project_state: Dict[str, Any],
    ) -> AgentOutput:
        """Run a specific agent."""
        project_state["current_date"] = datetime.utcnow().isoformat()
        
        agents = {
            "planning": self.planning_agent,
            "coordination": self.coordination_agent,
            "risk": self.risk_agent,
            "reporting": self.reporting_agent,
        }
        
        agent = agents.get(agent_name.lower())
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        return await agent.analyze(project_state)
    
    async def generate_executive_report(
        self,
        project_state: Dict[str, Any],
    ) -> str:
        """Generate comprehensive executive report using all agents."""
        project_state["current_date"] = datetime.utcnow().isoformat()
        
        # Run all analysis agents first
        import asyncio
        
        planning_output, coordination_output, risk_output = await asyncio.gather(
            self.planning_agent.analyze(project_state),
            self.coordination_agent.analyze(project_state),
            self.risk_agent.analyze(project_state),
        )
        
        # Generate comprehensive report
        return await self.reporting_agent.generate_full_report(
            project_state=project_state,
            other_agent_outputs=[planning_output, coordination_output, risk_output],
        )


# Singleton instance
orchestrator = AgentOrchestrator()


def get_orchestrator() -> AgentOrchestrator:
    """Get orchestrator instance for dependency injection."""
    return orchestrator
