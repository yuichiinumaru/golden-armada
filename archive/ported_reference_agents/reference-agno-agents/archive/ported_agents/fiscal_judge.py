from app.templates.base_agent import KhalaBaseAgent
from agno.tools.duckduckgo import DuckDuckGoTools

class FiscalJudgeAgent(KhalaBaseAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__(
            user_id=user_id,
            agent_name="FiscalJudge",
            model_id="gemini-2.5-pro", # Preference: pro
            system_prompt="""
IDENTITY: Julgador de Contencioso Sanitário.
MINDSET: Imparcialidade e Proporcionalidade.

TASK: Analise Acusação e Defesa presentes no Contexto.
1. Pese riscos vs. razoabilidade.
2. Emita veredito final.

OUTPUT_SCHEMA (JSON):
{
  "verdict": "MAINTAIN_INTERDICTION" | "CONVERT_TO_WARNING" | "RELEASE_WITH_CONDITIONS",
  "reasoning_summary": "string",
  "final_penalty": { "type": "string", "value_ufir": "string" },
  "required_actions": ["string"],
  "shared_facts": [
    { "key": "verdict.final", "value": "string", "confidence": 1.0, "category": "verdict" }
  ]
}
""",
            tools=[DuckDuckGoTools()]
        )
