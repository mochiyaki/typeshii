"""
Planning Agent - Converts goals into milestones and identifies sequencing risks.
"""
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.models import AgentOutput


class PlanningAgent(BaseAgent):
    """
    Planning Agent responsibilities:
    - Converts goals into milestones and dependencies
    - Identifies sequencing risks
    - Does NOT define implementation details
    """
    
    def __init__(self):
        super().__init__("PlanningAgent")
    
    @property
    def system_prompt(self) -> str:
        return """You are the Planning Agent in a PM Agentic Workflow system.
Your responsibility is to analyze project structure and planning:
- Evaluate milestone sequencing and dependencies
- Detect missing dependencies between tasks (e.g., matching logical flow)
- Flag unrealistic timelines or tight milestones

Output format for RECOMMENDATIONS (use exactly this structure):
TITLE: [Punchy, high-impact insight title, e.g., 'Missing dependencies in Milestone X']
PRIORITY: [low/medium/high/critical]
CATEGORY: planning
SUGGESTION: [Specific, brief action for the user]
REASON: [Short explanation of why this matters and the risk it poses]
AFFECTS: [comma-separated list of IDs]

Example Recommendation:
TITLE: No dependencies defined despite logical sequence
PRIORITY: high
CATEGORY: planning
SUGGESTION: Link 'Frontend Setup' to 'Backend Integration'
REASON: Tasks are being worked on in parallel without clear handoffs, risking integration failure.
AFFECTS: task_123, task_456

Be concise, punchy, and actionable. Match the 'Immediate Attention' style."""
    
    async def analyze(self, project_state: Dict[str, Any]) -> AgentOutput:
        """Analyze project planning and sequencing."""
        prompt = f"""Analyze this project's planning structure:

{self._format_project_state(project_state)}

Today's date: {project_state.get('current_date', 'Unknown')}

Evaluate:
1. Are milestones properly sequenced?
2. Are task dependencies correctly defined?
3. Are there any orphan tasks without milestones?
4. Are timelines realistic given dependencies?

Provide your analysis in the specified format."""

        response = await self.llm.structured_output(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.3,
        )
        
        # Parse response into structured output
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
            status_summary=status_summary or "Planning analysis complete",
            risks=risks,
            recommendations=recommendations,
        )
