
from app.templates.base_agent import KhalaBaseAgent


class DeepreasonerAgent(KhalaBaseAgent):
    def __init__(self, user_id: str = "system"):
        super().__init__(
            user_id=user_id,
            agent_name="DeepReasoner",
            model_id="gemini-2.5-flash",
            system_prompt="""Expert knowledge synthesizer specializing in extracting insights from multi-agent interactions, identifying patterns, and building collective intelligence. Masters cross-agent learning, best practice extraction, and continuous system improvement through knowledge management.
""",
            tools=[]
        )

# Entry point for testing
if __name__ == "__main__":
    import asyncio

    async def main():
        agent = DeepreasonerAgent(user_id="test_user")
        await agent.initialize()

        print(f"--- DeepreasonerAgent Initialized ---")
        response = await agent.chat("Hello!")
        print(f"Response: {response}")

        await agent.close()

    asyncio.run(main())
