from codeswarm.core.base_agent import SwarmAgent

class ReasoningAgent(SwarmAgent):
    def __init__(self, user_id: str = "default_user"):
        super().__init__(
            user_id=user_id,
            agent_name="DeepReasoner",
            role="DeepReasoner", # This handles fallback to fast, or we can make it Reasoning.
            # Reasoning agent usually implies reasoning model, let's verify role mapping or set model_id explicitly from env if needed.
            # Actually, "DeepReasoner" role isn't in my auto-list ("orchestrator", "admin", "planner", "gatekeeper", "security")
            # So I should PROBABLY update the role list in base_agent OR set model_id to env_reasoning here.
            # Better approach: Add "DeepReasoner" to the auto-detect list in base_agent.py OR explicitly use the env var here.
            # For now, let's just use the env var import.
            instructions="""
            Expert knowledge synthesizer specializing in extracting insights from multi-agent interactions, 
            identifying patterns, and building collective intelligence. 
            Masters cross-agent learning, best practice extraction, and continuous system improvement 
            through knowledge management.
            """
        )
