from codeswarm.core.base_agent import SwarmAgent

class ReasoningAgent(SwarmAgent):
    def __init__(self, user_id: str = "default_user"):
        super().__init__(
            user_id=user_id,
            agent_name="DeepReasoner",
            model_id="gemini-2.5-flash",
            instructions="""
            Expert knowledge synthesizer specializing in extracting insights from multi-agent interactions, 
            identifying patterns, and building collective intelligence. 
            Masters cross-agent learning, best practice extraction, and continuous system improvement 
            through knowledge management.
            """
        )
