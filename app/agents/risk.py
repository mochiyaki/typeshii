"""
Risk Agent - Monitors signals indicating delivery risk.
"""
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.models import AgentOutput


class RiskAgent(BaseAgent):
    """
    Risk Agent responsibilities:
    - Monitors signals indicating delivery risk
    - Assigns risk levels based on observable changes
    - Explains causes clearly
    """
    
    def __init__(self):
        super().__init__("RiskAgent")
    
    @property
    def system_prompt(self) -> str:
        return """You are the Risk Agent in a PM Agentic Workflow system.

Your responsibility is to identify and assess delivery risks:
- Monitor for blocked work
- Detect overdue tasks
- Identify dependency failures
- Track reduced velocity patterns
- Spot review bottlenecks
- Flag repeated failures

You must assign risk levels:
- LOW: Minor impact, easily addressed
- MEDIUM: Moderate impact, needs attention
- HIGH: Significant impact, urgent action needed
- CRITICAL: Severe impact, immediate intervention required

You must NOT:
- Speculate without observable signals
- Make implementation decisions
- Modify project content

Output format (use exactly this structure):
STATUS: [One-line risk summary]

RISKS:
- [LEVEL] [Risk description with observable cause]

RECOMMENDATIONS:
ACTION: [Specific risk mitigation action]
PRIORITY: [low/medium/high]
REASON: [Observable signals supporting this]
AFFECTS: [comma-separated list affected entities]

Focus on observable signals only. Be concise and evidence-based."""
    
    async def analyze(self, project_state: Dict[str, Any]) -> AgentOutput:
        """Analyze project risks based on observable signals."""
        prompt = f"""Analyze this project for delivery risks:

{self._format_project_state(project_state)}

Today's date: {project_state.get('current_date', 'Unknown')}

Identify risks from observable signals:
1. Overdue tasks (past due_date)
2. Tasks blocked for extended periods
3. Dependencies on incomplete tasks
4. Milestones at risk based on incomplete tasks
5. Velocity trends from recent events

Assign appropriate risk levels with clear justification.

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
            status_summary=status_summary or "Risk analysis complete",
            risks=risks,
            recommendations=recommendations,
        )
