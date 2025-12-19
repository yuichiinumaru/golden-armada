import pytest
import asyncio
from app.agents.bi_detective import BIDetectiveAgent
from app.agents.bi_janitor import BIJanitorAgent
from app.agents.bi_architect import BIArchitectAgent
from app.agents.bi_analyst import BIAnalystAgent

@pytest.mark.asyncio
async def test_bi_agents_initialization():
    agents = [
        BIDetectiveAgent(),
        BIJanitorAgent(),
        BIArchitectAgent(),
        BIAnalystAgent()
    ]
    
    for agent in agents:
        print(f"Testing initialization of {agent.agent_name}...")
        # Mocking initialize to avoid actual DB connection if needed, 
        # but here we want to see if it runs. 
        # If Khala is not reachable, it might fail.
        # For this smoke test, we can try-except the connection part or just check instantiation.
        
        assert agent.agent_name in ["BIDetective", "BIJanitor", "BIArchitect", "BIAnalyst"]
        assert agent.user_id == "default_user"
        
        # We skip actual .initialize() in unit test if no DB is present, 
        # but we can check if the object is created correctly.
        print(f"{agent.agent_name} instantiated successfully.")

if __name__ == "__main__":
    asyncio.run(test_bi_agents_initialization())
