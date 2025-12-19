from codeswarm.core.base_agent import SwarmAgent
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools

class LabelInspectorAgent(SwarmAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__()
        self.agent = Agent(
            user_id=user_id,
            description="Label Inspector",
            model=self.get_model("gemini-2.5-flash"),
            instructions="""
AGENT_PROFILE:
  ID: anvisa_label_inspector_v2
  ROLE: Food Safety Auditor (RDC 429/2020 & IN 75/2020)

CHECKLIST:
  1. Tabela Nutricional (Presence, Legibility, White Background)
  2. Lista de Ingredientes (Order descending)
  3. Alergênicos (Bold, Uppercase "ALÉRGICOS: ...")
  4. Lupa Frontal (Alto em Açúcar/Sódio/Gordura) if applicable.

OUTPUT_SCHEMA (JSON):
  {
    "product_name": "string",
    "compliance": {
      "tabela_nutricional": "PASS" | "FAIL" | "MISSING",
      "ingredientes": "PASS" | "FAIL",
      "alergenicos": "PASS" | "FAIL",
      "rotulagem_frontal": "PASS" | "FAIL" | "NOT_REQUIRED"
    },
    "violations": [
      { "rule": "string", "observation": "string", "severity": "LOW" | "HIGH" }
    ],
    "verdict": "COMPLIANT" | "NON_COMPLIANT"
  }
""",
            tools=[DuckDuckGoTools()],
            show_tool_calls=True,
            markdown=True,
            monitoring=True,
        )
