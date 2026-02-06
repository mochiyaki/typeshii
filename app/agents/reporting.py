"""
Reporting Agent - Generates structured summaries for stakeholders.
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.models import AgentOutput


class ReportingAgent(BaseAgent):
    """
    Reporting Agent responsibilities:
    - Generates structured summaries for stakeholders
    - Focuses on status, risks, and next actions
    """
    
    def __init__(self):
        super().__init__("ReportingAgent")
    
    @property
    def system_prompt(self) -> str:
        return """You are the Reporting Agent in a PM Agentic Workflow system.
Your responsibility is to generate clear summaries for stakeholders:
- Summarize overall project health
- Recommend critical next actions

Output format for RECOMMENDATIONS (use exactly this structure):
TITLE: [Punchy header, e.g., 'Project on track for Milestone 2']
PRIORITY: [low/medium/high/critical]
CATEGORY: reporting
SUGGESTION: [Operational next step]
REASON: [Short justification]
AFFECTS: [Entities]

Be extremely concise and operational."""
    
    async def analyze(self, project_state: Dict[str, Any]) -> AgentOutput:
        """Generate stakeholder summary."""
        prompt = f"""Generate a stakeholder summary for this project:

{self._format_project_state(project_state)}

Today's date: {project_state.get('current_date', 'Unknown')}

Create a clear, concise summary in the specified format."""

        response = await self.llm.structured_output(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.4,
        )
        
        # Parse response
        status_summary = ""
        risks = []
        lines = response.split("\n")
        in_risks = False
        
        for line in lines:
            line = line.strip()
            if line.startswith("STATUS:"):
                status_summary = line.replace("STATUS:", "").strip()
            elif line == "RISKS:":
                in_risks = True
            elif line.startswith("TITLE:"):
                in_risks = False
            elif in_risks and line.startswith("-"):
                risks.append(line[1:].strip())
        
        return AgentOutput(
            agent_name=self.name,
            status_summary=status_summary or "Report generated",
            risks=risks,
            recommendations=self._parse_recommendations(response),
        )
    
    async def generate_full_report(
        self,
        project_state: Dict[str, Any],
        other_agent_outputs: List[AgentOutput],
    ) -> str:
        """Generate a comprehensive report including insights from other agents."""
        # Combine insights from other agents
        all_recommendations = []
        
        for output in other_agent_outputs:
            all_recommendations.extend(output.recommendations)
        
        # Add aggregated insights to context
        aggregated_context = "\nAGGREGATED AGENT INSIGHTS:\n"
        if all_recommendations:
            aggregated_context += "Key Recommendations:\n"
            for rec in all_recommendations[:8]:
                aggregated_context += f"  - [{rec.priority}] {rec.title}: {rec.suggestion}\n"
        
        prompt = f"""Generate an executive stakeholder report:

{self._format_project_state(project_state)}

{aggregated_context}

Today's date: {project_state.get('current_date', 'Unknown')}"""

        return await self.llm.structured_output(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.4,
        )
