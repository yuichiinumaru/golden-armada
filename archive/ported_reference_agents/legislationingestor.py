
from app.templates.base_agent import KhalaBaseAgent


class LegislationingestorAgent(KhalaBaseAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__(
            user_id=user_id,
            agent_name="LegislationIngestor",
            model_id="gemini-2.5-flash",
            system_prompt="""Process legal texts and ingest them into Khala Knowledge Graph. Structure laws into Article, Section, Paragraph nodes.
""",
            tools=[]
        )

# Entry point for testing
if __name__ == "__main__":
    import asyncio

    async def main():
        agent = LegislationingestorAgent(user_id="test_user")
        await agent.initialize()

        print(f"--- LegislationingestorAgent Initialized ---")
        response = await agent.chat("Hello!")
        print(f"Response: {response}")

        await agent.close()

    asyncio.run(main())
