
import os
import asyncio
from dotenv import load_dotenv
from codeswarm.core.base_agent import SwarmAgent

# Load environment variables
load_dotenv()
os.environ["GENAI_API_KEYS"] = "dummy_key_for_testing"

async def verify_model_selection():
    print("--- Verifying Model Selection Logic ---")
    
    # Expected models from .env (or defaults if loading fails, but we assume .env is loaded)
    # We'll print what we see in the class to be sure
    
    # 1. Test Fast Agent (Default)
    fast_agent = SwarmAgent(
        user_id="test_user", 
        agent_name="FastWorker", 
        role="Coder",
        instructions="Coding task"
    )
    print(f"[Fast Agent] Role: {fast_agent.role}")
    print(f"[Fast Agent] Selected Model: {fast_agent.model_id}")
    
    # 2. Test Reasoning Agent (Role-based)
    reasoning_agent = SwarmAgent(
        user_id="test_user", 
        agent_name="Boss", 
        role="Orchestrator",
        instructions="Planning task"
    )
    print(f"[Reasoning Agent] Role: {reasoning_agent.role}")
    print(f"[Reasoning Agent] Selected Model: {reasoning_agent.model_id}")
    
    # 3. Test Reasoning Agent (Security Role)
    sec_agent = SwarmAgent(
        user_id="test_user", 
        agent_name="Gatekeeper", 
        role="Security",
        instructions="Security task"
    )
    print(f"[Security Agent] Role: {sec_agent.role}")
    print(f"[Security Agent] Selected Model: {sec_agent.model_id}")

    # 4. Test Explicit Override
    override_model = "gemini-2.5-flash-lite"
    custom_agent = SwarmAgent(
        user_id="test_user", 
        agent_name="CustomWorker", 
        role="Worker", 
        model_id=override_model,
        instructions="Custom task"
    )
    print(f"[Custom Agent] Explicit Model: {custom_agent.model_id}")

    # Verification checks
    fast_model_env = os.getenv("GEMINI_MODEL_FAST", "gemini-3.0-flash")
    reasoning_model_env = os.getenv("GEMINI_MODEL_REASONING", "gemini-3.0-pro")

    failed = False
    
    if fast_agent.model_id != fast_model_env:
        print(f"FAIL: Fast Agent model {fast_agent.model_id} != {fast_model_env}")
        failed = True
        
    if reasoning_agent.model_id != reasoning_model_env:
        print(f"FAIL: Reasoning Agent model {reasoning_agent.model_id} != {reasoning_model_env}")
        failed = True

    if sec_agent.model_id != reasoning_model_env:
        print(f"FAIL: Security Agent model {sec_agent.model_id} != {reasoning_model_env}")
        failed = True
        
    if custom_agent.model_id != override_model:
        print(f"FAIL: Custom Agent model {custom_agent.model_id} != {override_model}")
        failed = True

    if not failed:
        print("\n✅ All Model Selection Tests Passed!")
    else:
        print("\n❌ Checking Failed.")

if __name__ == "__main__":
    asyncio.run(verify_model_selection())
