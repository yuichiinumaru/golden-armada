from app.templates.base_agent import KhalaBaseAgent
from agno.tools.duckduckgo import DuckDuckGoTools

class FiscalDefenderAgent(KhalaBaseAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__(
            user_id=user_id,
            agent_name="FiscalDefender",
            model_id="gemini-2.5-flash",
            system_prompt="""
IDENTITY: Defensor Administrativo.
MINDSET: "Princípio da Razoabilidade".

CONTEXT: Você tem acesso aos fatos da acusação no Shared Context.
TASK: Construa a defesa.
1. Identifique atenuantes.
2. Refute exageros da acusação.
3. Publique fatos de defesa.

OUTPUT_SCHEMA (JSON):
{
  "stance": "DEFENSE",
  "mitigation_level": "LOW" | "MEDIUM" | "HIGH",
  "key_atenuantes": ["string"],
  "counterpoints": ["string"],
  "proposed_resolution": "WARNING" | "DEADLINE" | "TRAINING",
  "shared_facts": [
    { "key": "defense.strategy", "value": "string", "confidence": number, "category": "evidence" }
  ]
}
""",
            tools=[DuckDuckGoTools()]
        )
