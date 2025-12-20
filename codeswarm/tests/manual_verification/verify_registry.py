import sys
import os
import logging

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from codeswarm.core.registry import AgentRegistry

logging.basicConfig(level=logging.INFO)

def verify_registry():
    print("--- Verifying AgentRegistry Auto-Categorization ---")
    registry = AgentRegistry()
    registry.load_agents()
    
    categories = registry.get_categories()
    print(f"\nDiscovered Categories: {categories}")
    
    if not categories:
        print("ERROR: No categories found!")
        return

    expected_categories = ['backend', 'frontend', 'data', 'ops']
    missing = [c for c in expected_categories if c not in categories]
    
    if missing:
        print(f"WARNING: Expected categories missing: {missing}")
        # This might be fine if we haven't migrated all agents yet, but we expect some.
    
    print("\n--- Sample Agents per Category ---")
    for cat in categories:
        agents = registry.get_agents_by_category(cat)
        print(f"Category '{cat}': {len(agents)} agents")
        # Print first 3
        for agent in agents[:3]:
            print(f"  - {agent}")
            
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_registry()
