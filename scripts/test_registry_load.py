import sys
import os
import logging

# Ensure codeswarm is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codeswarm.core.registry import AgentRegistry

logging.basicConfig(level=logging.INFO)

def test_registry():
    print("Testing AgentRegistry...")
    registry = AgentRegistry()
    registry.load_agents()
    
    print(f"\nLoaded Agents: {len(registry.agents)}")
    for name in registry.list_agents():
        print(f" - {name}")

    if "OrchestratorAgent" in registry.agents:
        print("\nSUCCESS: OrchestratorAgent found.")
    else:
        print("\nFAILURE: OrchestratorAgent NOT found.")

    if len(registry.agents) > 0:
        print("SUCCESS: Agents loaded.")
    else:
        print("FAILURE: No agents loaded.")

if __name__ == "__main__":
    test_registry()
