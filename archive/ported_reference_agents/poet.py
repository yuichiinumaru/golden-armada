
from app.templates.base_agent import KhalaBaseAgent
from agno.tools.calculator import CalculatorTools
# Import other tools as needed

class PoetAgent(KhalaBaseAgent):
    def __init__(self, user_id: str):
        super().__init__(
            user_id=user_id,
            agent_name="Poet",
            model_id="gemini-2.5-flash",
            system_prompt="You are a poet who speaks in rhymes.",
            tools=[CalculatorTools()] # Default tool, customize as needed
        )

# Entry point for direct execution
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = PoetAgent(user_id="test_user")
        await agent.initialize()
        
        print(f"--- PoetAgent Initialized ---")
        response = await agent.chat("Hello, who are you?")
        print(f"Response: {response}")
        
        await agent.close()

    asyncio.run(main())
