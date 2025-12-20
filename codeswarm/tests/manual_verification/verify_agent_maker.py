import asyncio
import os
from dotenv import load_dotenv

# Load env for API keys
load_dotenv()
# Dummy key if not present to avoid init error during import if Agno checks immediately (it usually checks on run)
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "dummy"

from codeswarm.services.agent_maker import agent_maker

async def verify_agent_maker():
    print("Verifying AgentMakerService...")
    
    draft = {
        "name": "TestAgent",
        "description": "A test agent",
        "prompt": "I want an agent that can search the web and summarize news about AI."
    }
    
    print(f"Input Draft: {draft}")
    
    try:
        # engineering currently mocks or uses AI. 
        # CAUTION: If no API key, AI calls will fail.
        # We expect it to fallback to heuristics or work if key is valid.
        result = await agent_maker.engineer_agent(draft)
        
        print("Engineer Result:")
        print(f"Name: {result['name']}")
        print(f"Tools: {result['tools']}")
        print(f"Optimized Prompt Header: {result['prompt'][:50]}...")
        
        # Check heuristics
        tools_str = str(result['tools'])
        if "DuckDuckGoTools" in tools_str or "Newspaper4kTools" in tools_str:
            print("SUCCESS: Heuristics/AI selected search/news tools.")
        else:
            print("WARNING: Expected search/news tools not found (checks heuristics).")
            
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    asyncio.run(verify_agent_maker())
