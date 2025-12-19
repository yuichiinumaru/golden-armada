from codeswarm.core.base_agent import SwarmAgent
from agno.agent import Agent
from agno.tools.calculator import CalculatorTools

class PoetAgent(SwarmAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__()
        self.agent = Agent(
            user_id=user_id,
            description="Poet",
            model=self.get_model("gemini-2.5-flash"),
            instructions="You are a poet who speaks in rhymes.",
            tools=[CalculatorTools()],
            show_tool_calls=True,
            markdown=True,
            monitoring=True,
        )
