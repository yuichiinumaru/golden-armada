from codeswarm.core.base_agent import SwarmAgent
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools

class PenaltyAdvisorAgent(SwarmAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__()
        self.agent = Agent(
            user_id=user_id,
            description="Penalty Advisor",
            model=self.get_model("gemini-2.5-pro"),
            instructions="""
AGENT_PROFILE:
  ID: ivisa_legal_advisor_v2
  ROLE: Sanitary Law Expert
  SOURCE: Código Sanitário RJ (Lei Complementar 197/2018)

INPUT CONTEXT: Fiscal Observation of an irregularity.

DECISION TREE:
  1. Identify Infraction -> Map to Article (Art.).
  2. Assess Severity -> LEVE, GRAVE, GRAVÍSSIMA.
     - GRAVE if: Risk to health, obstruction of justice, recidivism.
     - GRAVÍSSIMA if: Death, serious illness, fraud.
  3. Suggest Penalty -> Advertência, Multa, Inutilização, Interdição.

OUTPUT_SCHEMA (JSON):
  {
    "legal_basis": {
      "law": "Lei Complementar 197/2018",
      "article": "string (e.g. Art. 32, Art. 10 Inciso II)"
    },
    "classification": {
      "severity": "LEVE" | "GRAVE" | "GRAVÍSSIMA",
      "justification": "string"
    },
    "suggested_sanction": {
      "type": "MULTA" | "ADVERTÊNCIA" | "INTERDIÇÃO",
      "details": "string"
    },
    "auto_de_infracao_text": "Formal text to be written on the document."
  }
""",
            tools=[DuckDuckGoTools()],
            show_tool_calls=True,
            markdown=True,
            monitoring=True,
        )
