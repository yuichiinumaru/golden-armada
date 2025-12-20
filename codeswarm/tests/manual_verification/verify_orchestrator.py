import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

from codeswarm.agents.orchestrator_agent import OrchestratorAgent

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

async def main():
    print("--- Verifying Orchestrator Routing Logic ---")
    
    # Instantiate Orchestrator
    try:
        orchestrator = OrchestratorAgent(user_id="test_user")
    except Exception as e:
        print(f"Failed to init orchestrator: {e}")
        return

    # User Request that should trigger 'backend' category
    request = "I need a scalable FastAPI backend for a todo list application with PostgreSQL."
    
    print(f"\nSending Request: '{request}'")
    
    # Run Plan Workflow
    try:
        plan = await orchestrator.plan_workflow(request)
        print(f"\n--- Plan Generated ---")
        print(plan)
        
        # We can't easily assert on internal logging without capturing it, 
        # but the stdout logs should show "Routing Request to Categories: ..."
        
    except Exception as e:
        print(f"Planning failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
