from codeswarm.core.base_agent import SwarmAgent

class PromptEngineerAgent(SwarmAgent):
    def __init__(self, user_id: str = "system"):
        instructions = """
You are an expert Prompt Engineer using the ACE Ultra methodology.
Your goal is to optimize System Prompts for LLMs (specifically Gemini 2.5).

INPUT: Draft System Prompt and List of Tools (Native + MCP).

TASK:
1. Refine the structure (Identity, Context, Task, Constraints, Output Format).
2. Inject instructions on how to use the provided Tools.
3. Optimize for clarity and density.

OUTPUT: The fully optimized System Prompt (Markdown).
"""
        super().__init__(
            user_id=user_id,
            agent_name="PromptEngineer",
            role="Prompt Engineer",
            model_id="gemini-2.5-pro", # Using Pro for better reasoning
            instructions=instructions
        )
