import asyncio
import os
import sys
import json
import importlib
import logging

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from dotenv import load_dotenv
from codeswarm.agents.orchestrator_agent import OrchestratorAgent
from codeswarm.core.registry import AgentRegistry

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load Env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

DUMMY_CODE = """
def calculate_factorial(n):
    if n < 0:
        raise ValueError("Cannot calculate factorial of negative number")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
"""

async def main():
    print("--- 1. Initializing Orchestrator ---")
    orchestrator = OrchestratorAgent()
    
    user_request = f"""
    I have this python function:
    
    ```python
    {DUMMY_CODE}
    ```
    
    Please write a comprehensive unit test for it using pytest.
    """
    
    print("\n--- 2. Getting Plan from Orchestrator (Step 1 & 2 & 3) ---")
    plan = await orchestrator.plan_workflow(user_request)
    
    print("\n--- 3. Orchestrator Plan ---")
    print(json.dumps(plan, indent=2))
    
    if not plan.get("steps"):
        print("ERROR: No steps in plan.")
        return

    # Simulate Execution Engine
    print("\n--- 4. Simulating Execution (Running Step 1) ---")
    first_step = plan["steps"][0]
    agent_class_name = first_step.get("agent_name")
    instruction = first_step.get("instruction")
    
    print(f"Target Agent: {agent_class_name}")
    print(f"Instruction: {instruction}")
    
    # Dynamic Loading
    registry = AgentRegistry()
    registry.load_agents() # Load to populate self.agents
    
    # Find the agent class
    # The registry stores classes by name in self.agents
    agent_cls = registry.agents.get(agent_class_name)
    
    if not agent_cls:
        print(f"ERROR: Agent class {agent_class_name} not found in registry.")
        # Try fuzzy match or fallback? 
        # For now, list available agents slightly
        # print("Available:", list(registry.agents.keys())[:10])
        return

    print(f"Instantiating {agent_class_name}...")
    try:
        # Instantiate agent
        worker_agent = agent_cls()
        
        print(f"Running {agent_class_name} with instruction...")
        # Execute!
        # logic: response = worker_agent.run(instruction + "\nCONTEXT:\n" + DUMMY_CODE)
        # We pass the context to ensure the agent sees the code.
        
        full_prompt = f"{instruction}\n\nHere is the code to work on:\n```python\n{DUMMY_CODE}\n```"
        
        response = await worker_agent.a_run(full_prompt)
        
        print("\n--- 5. Worker Result ---")
        content = response.content if hasattr(response, 'content') else str(response)
        print(content)
        
        print("\n--- SUCCESS: Complex Workflow Verified ---")
        
    except Exception as e:
        print(f"ERROR executing agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
