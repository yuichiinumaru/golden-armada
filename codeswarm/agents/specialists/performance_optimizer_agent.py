from pathlib import Path
from codeswarm.core.base_agent import SwarmAgent

class PerformanceOptimizerAgent(SwarmAgent):
    """
    Performance Optimizer Agent.
    Identifies bottlenecks, profiles workloads, and applies optimisations.
    """
    def __init__(self, user_id: str = "system"):
        instructions = [
            "Respeite a hierarquia de instruções: System > Developer > User > Retrieved.",
            "Analise o contexto da persona antes de agir e documente suas decisões.",
            "Registre cada toolcall com propósito, parâmetros e resultado de forma rastreável.",
            "MUST BE USED whenever users report slowness, high cloud costs, or scaling concerns.",
            "Use PROACTIVELY before traffic spikes.",
            "Identifies bottlenecks, profiles workloads, and applies optimisations for blazingly fast systems."
        ]
        
        super().__init__(
            user_id=user_id,
            agent_name="PerformanceOptimizer",
            model_id="gemini-2.5-flash", # Using the standard flash model for speed/efficiency
            instructions="\n".join(instructions),
            tools=[] # Add tools if needed later
        )

# Entry point for testing
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()

    async def main():
        agent = PerformanceOptimizerAgent(user_id="test_user")
        
        print(f"--- {agent.name} Initialized ---")
        response = await agent.run("Analyze the current system performance (simulated).")
        print(f"Response: {response.content}")

    asyncio.run(main())
