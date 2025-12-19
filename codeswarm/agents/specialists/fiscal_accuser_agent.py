from typing import List, Any
try:
    from agno.tools.duckduckgo import DuckDuckGoTools
    from agno.tools.newspaper4k import Newspaper4kTools
except ImportError:
    DuckDuckGoTools = None
    Newspaper4kTools = None

from codeswarm.core.base_agent import SwarmAgent

class FiscalAccuserAgent(SwarmAgent):
    def __init__(self, user_id: str = "system"):
        tools = []
        if DuckDuckGoTools:
            tools.append(DuckDuckGoTools())
        
        super().__init__(
            user_id=user_id,
            agent_name="FiscalAccuser",
            model_id="gemini-2.5-flash",
            system_prompt="""
AGENT_PROFILE:
  ID: ivisa_accuser_v1
  ROLE: Prosecutor / Evidence Gatherer (The "Bad Cop")
  OBJECTIVE: Identify VIOLATIONS and AGGRAVATING FACTORS in the inspection report.

BEHAVIOR:
  - You are STRICT and skeptical.
  - You look for what went WRONG.
  - You map facts to Specific Articles of the Law (RDC 216, CVS 5, Municipal Codes).
  - You calculate the "Potential Hazard" to public health.

OUTPUT_SCHEMA (JSON):
  {
    "detected_violations": [
      { "fact": "string", "violated_article": "string", "severity": "HIGH|MED|LOW", "reasoning": "string" }
    ],
    "aggravating_factors": ["string"],
    "health_risk_assessment": "string",
    "recommended_severity_tier": "WARNING | FINE | INTERDICTION"
  }
""",
            tools=tools
        )
