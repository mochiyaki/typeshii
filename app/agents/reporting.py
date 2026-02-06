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

Your responsibility is to generate clear, actionable summaries for stakeholders:
- Summarize current project status
- Highlight key risks and blockers
- Recommend next actions

Output must be:
- Concise
- Operational
- Neutral in tone
- Focused on actions and outcomes

Use this exact format:

STATUS: [Overall project health in one line]

PROJECT SUMMARY:
[2-3 sentences on current state]

COMPLETED THIS PERIOD:
- [Item 1]
- [Item 2]

IN PROGRESS:
- [Item 1 with assignee]
- [Item 2 with assignee]

RISKS:
- [Risk with severity]

RECOMMENDATIONS:
ACTION: [Next recommended action]
PRIORITY: [low/medium/high]
REASON: [Brief justification]
AFFECTS: [Stakeholders or entities]

Be extremely concise. Stakeholders need instant clarity."""
    
    async def analyze(self, project_state: Dict[str, Any]) -> AgentOutput:
        """Generate stakeholder summary."""
        prompt = f"""Generate a stakeholder summary for this project:

{self._format_project_state(project_state)}

Today's date: {project_state.get('current_date', 'Unknown')}

Create a clear, concise summary that answers:
1. What is the overall project health?
2. What was completed recently?
3. What is currently in progress?
4. What are the key risks?
5. What action should be taken next?

Provide your summary in the specified format."""

        response = await self.llm.structured_output(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.4,
        )
        
        # Parse response
        lines = response.split("\n")
        status_summary = ""
        risks = []
        in_risks = False
        
        for line in lines:
            line = line.strip()
            if line.startswith("STATUS:"):
                status_summary = line.replace("STATUS:", "").strip()
            elif line == "RISKS:" or line == "RISKS":
                in_risks = True
            elif line.startswith("RECOMMENDATIONS:") or line.startswith("ACTION:"):
                in_risks = False
            elif in_risks and line.startswith("-"):
                risks.append(line[1:].strip())
        
        recommendations = self._parse_recommendations(response)
        
        return AgentOutput(
            agent_name=self.name,
            status_summary=status_summary or "Report generated",
            risks=risks,
            recommendations=recommendations,
        )
    
    async def generate_full_report(
        self,
        project_state: Dict[str, Any],
        other_agent_outputs: List[AgentOutput],
    ) -> str:
        """Generate a comprehensive report including insights from other agents."""
        # Combine insights from other agents
        all_risks = []
        all_recommendations = []
        
        for output in other_agent_outputs:
            all_risks.extend(output.risks)
            all_recommendations.extend(output.recommendations)
        
        # Add aggregated insights to context
        aggregated_context = "\nAGGREGATED AGENT INSIGHTS:\n"
        if all_risks:
            aggregated_context += "Key Risks Identified:\n"
            for risk in set(all_risks):
                aggregated_context += f"  - {risk}\n"
        
        if all_recommendations:
            aggregated_context += "Recommended Actions:\n"
            for rec in all_recommendations[:5]:  # Top 5 recommendations
                aggregated_context += f"  - [{rec.priority}] {rec.action}\n"
        
        prompt = f"""Generate an executive summary combining project state and agent insights:

{self._format_project_state(project_state)}

{aggregated_context}

Today's date: {project_state.get('current_date', 'Unknown')}

Create a comprehensive but concise stakeholder report."""

        return await self.llm.structured_output(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.4,
        )
