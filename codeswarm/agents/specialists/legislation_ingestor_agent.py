from codeswarm.core.base_agent import SwarmAgent
from agno.agent import Agent

class LegislationIngestorAgent(SwarmAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__()
        self.agent = Agent(
            user_id=user_id,
            description="Legislation Ingestor",
            model=self.get_model("gemini-2.5-flash"),
            instructions="""Process legal texts and ingest them into Khala Knowledge Graph. Structure laws into Article, Section, Paragraph nodes.""",
            show_tool_calls=True,
            markdown=True,
            monitoring=True,
        )
