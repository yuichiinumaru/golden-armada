import os
import sys
import importlib.util
import logging
import glob
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add the packages directory to sys.path to allow importing from void_engine
# Assuming this runs from services/agent_os
PACKAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../packages"))
if PACKAGES_DIR not in sys.path:
    sys.path.append(PACKAGES_DIR)

from app.lib.khala_client import KhalaClient
from app.templates.base_agent import KhalaBaseAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Registry to discover, load, and manage agents from the Golden Armada.
    """
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.khala_client = KhalaClient()
        # Updated path to the migrated legacy agents
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # services/agent_os
        self.agents_dir = os.path.join(base_dir, "legacy_agents/golden_armada/agno-agents")

    async def load_agents(self):
        """Dynamically load all agents from the agents directory."""
        logger.info(f"Loading agents from {self.agents_dir}...")
        
        if not os.path.exists(self.agents_dir):
            logger.error(f"Agents directory not found: {self.agents_dir}")
            return

        # Find all python files in the directory
        agent_files = glob.glob(os.path.join(self.agents_dir, "*_agent.py"))
        
        for file_path in agent_files:
            try:
                self._load_agent_from_file(file_path)
            except Exception as e:
                logger.error(f"Failed to load agent from {file_path}: {e}")

        logger.info(f"Loaded {len(self.agents)} agents.")

    def _load_agent_from_file(self, file_path: str):
        """Load a single agent module and instantiate the agent."""
        module_name = os.path.basename(file_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Look for a class that inherits from KhalaBaseAgent or follows the pattern
            # For now, we assume the file defines a class matching the filename (CamelCase)
            # or exports an 'agent' object or a factory function.
            
            # Heuristic: Find the first class that ends with 'Agent'
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and attribute_name.endswith("Agent") and attribute_name != "KhalaBaseAgent" and attribute_name != "BaseAgent":
                    # Instantiate the agent
                    # We assume the constructor takes 'khala' or we inject it
                    try:
                        # Check if it accepts khala
                        # For now, we just instantiate it. If it needs khala, we might need to refactor the agents first.
                        # But the plan says "Refactor Agents" is next. So here we just try to load.
                        # If the agent is not yet refactored, this might fail or we just store the class.
                        
                        # Store the class for now, instantiation might happen per request or here if singleton
                        self.agents[module_name] = attribute
                        logger.debug(f"Registered agent class: {attribute_name} from {module_name}")
                        return
                    except Exception as e:
                        logger.warning(f"Found agent class {attribute_name} but failed to register: {e}")

    def get_agent(self, agent_name: str) -> Optional[Any]:
        """Get an agent instance by name."""
        agent_class = self.agents.get(agent_name)
        if agent_class:
            # Instantiate with KhalaClient
            # This assumes the agent class accepts khala_client in __init__
            # If not refactored yet, this will be part of the next phase
            return agent_class(khala=self.khala_client)
        return None

    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self.agents.keys())
