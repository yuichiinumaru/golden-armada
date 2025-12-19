
from app.templates.base_agent import KhalaBaseAgent


class ApexoptimizerAgent(KhalaBaseAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__(
            user_id=user_id,
            agent_name="ApexOptimizer",
            model_id="gemini-2.5-flash",
            system_prompt="""MUST BE USED whenever users report slowness, high cloud costs, or scaling concerns. Use PROACTIVELY before traffic spikes. Identifies bottlenecks, profiles workloads, and applies optimisations for blazingly fast systems.
""",
            tools=[]
        )

# Entry point for testing
if __name__ == "__main__":
    import asyncio

    async def main():
        agent = ApexoptimizerAgent(user_id="test_user")
        await agent.initialize()

        print(f"--- ApexoptimizerAgent Initialized ---")
        response = await agent.chat("Hello!")
        print(f"Response: {response}")

        await agent.close()

    asyncio.run(main())
