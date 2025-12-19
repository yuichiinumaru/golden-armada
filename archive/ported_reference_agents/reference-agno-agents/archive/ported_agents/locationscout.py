
from app.templates.base_agent import KhalaBaseAgent
from agno.tools.duckduckgo import DuckDuckGoTools

class LocationscoutAgent(KhalaBaseAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__(
            user_id=user_id,
            agent_name="LocationScout",
            model_id="gemini-2.5-flash",
            system_prompt="""Expert Location Scout and Geographic Analyst. Search for locations, analyze maps, coordinates, and spatial data.
""",
            tools=[DuckDuckGoTools()]
        )

# Entry point for testing
if __name__ == "__main__":
    import asyncio

    async def main():
        agent = LocationscoutAgent(user_id="test_user")
        await agent.initialize()

        print(f"--- LocationscoutAgent Initialized ---")
        response = await agent.chat("Hello!")
        print(f"Response: {response}")

        await agent.close()

    asyncio.run(main())
