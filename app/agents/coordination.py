"""
Coordination Agent - Tracks task progress and ownership, detects stalled work.
"""
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.models import AgentOutput


class CoordinationAgent(BaseAgent):
    """
    Coordination Agent responsibilities:
    - Tracks task progress and ownership
    - Detects stalled work or missing handoffs
    - Suggests communication actions
    """
    
    def __init__(self):
        super().__init__("CoordinationAgent")
    
    @property
    def system_prompt(self) -> str:
        return """You are the Coordination Agent in a PM Agentic Workflow system.
Your responsibility is to ensure smooth task flow and team coordination:
- Track task progress and ownership
- Detect unassigned tasks or resource gaps
- Identify stalled or blocked work without documentation

Output format for RECOMMENDATIONS (use exactly this structure):
TITLE: [Punchy header, e.g., 'Unassigned task risks Shoppin...']
PRIORITY: [low/medium/high/critical]
CATEGORY: coordination
SUGGESTION: [Brief action, e.g., 'Assign dev_02 to Stripe Integration']
REASON: [Why this matters, e.g., 'Payment logic is blocking checkout milestone']
AFFECTS: [comma-separated IDs]

Be concise and punchy. Match the 'Immediate Attention' UI style."""
    
    async def analyze(self, project_state: Dict[str, Any]) -> AgentOutput:
        """Analyze project coordination and task flow."""
        prompt = f"""Analyze this project's coordination state:

{self._format_project_state(project_state)}

Today's date: {project_state.get('current_date', 'Unknown')}

Evaluate:
1. Are there tasks in_progress for too long without updates?
2. Are there completed tasks whose dependents haven't started?
3. Are there unassigned tasks that should be assigned?
4. Are there blocked tasks without documented blockers?

Identify stalled work and suggest communication actions to improve flow.

Provide your analysis in the specified format."""

        response = await self.llm.structured_output(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.3,
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
            status_summary=status_summary or "Coordination analysis complete",
            risks=risks,
            recommendations=recommendations,
        )
