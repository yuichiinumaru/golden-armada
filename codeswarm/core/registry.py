import os
import sys
import importlib.util
import logging
import glob
from typing import Dict, Any, List, Optional, Type
from codeswarm.core.base_agent import SwarmAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Registry to discover, load, and manage agents dynamically.
    Scans specific directories for SwarmAgent implementations.
    """
    def __init__(self):
        self.agents: Dict[str, Type[SwarmAgent]] = {}
        # Base directory of the package
        self.base_dir = os.path.dirname(os.path.dirname(__file__)) # codeswarm/
        
        # Directories to scan relative to codeswarm/
        self.scan_dirs = [
            "agents/armada",
            "agents/specialists",
            "agents" # For things like gatekeeper or orchestrator if they are direct
        ]

    def load_agents(self):
        """Dynamically load all agents from the configured directories."""
        count = 0
        for rel_dir in self.scan_dirs:
            abs_dir = os.path.join(self.base_dir, rel_dir)
            if not os.path.exists(abs_dir):
                logger.debug(f"Skipping non-existent directory: {abs_dir}")
                continue
                
            logger.info(f"Scanning for agents in {abs_dir}...")
            
            # Find all python files
            agent_files = glob.glob(os.path.join(abs_dir, "*_agent.py"))
            # Also include named files that might not end in _agent if specifically known, 
            # but for armada they generally follow conventions.
            
            for file_path in agent_files:
                try:
                    self._load_agent_from_file(file_path)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to load agent from {file_path}: {e}")

        logger.info(f"Total agents loaded in registry: {len(self.agents)}")

    def _load_agent_from_file(self, file_path: str):
        """Load a single agent module and register the class."""
        module_name = os.path.basename(file_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find SwarmAgent subclasses
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if (isinstance(attribute, type) and 
                    issubclass(attribute, SwarmAgent) and 
                    attribute is not SwarmAgent):
                    
                    # Use a registry key. Ideally the agent has a NAME attribute, 
                    # but if not we use class name or a convention.
                    # For now using Class Name as the key.
                    self.agents[attribute_name] = attribute
                    logger.debug(f"Registered agent: {attribute_name}")

    def get_agent(self, agent_name: str, user_id: str = "default") -> Optional[SwarmAgent]:
        """Instantiate and get an agent by class name."""
        agent_class = self.agents.get(agent_name)
        if agent_class:
            return agent_class(user_id=user_id)
        return None

    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self.agents.keys())

    def get_agents_info(self) -> List[Dict[str, Any]]:
        """Returns detailed info for all agents, useful for UI."""
        results = []
        
        # Add a static entry for the Gatekeeper if needed, or dynamically checks
        # For now, we iterate over registered agents.
        
        for name, agent_cls in self.agents.items():
            # Instantiate to get properties? Or inspect class attributes? 
            # Ideally we inspect class attributes if possible, or instantiate a temporay one.
            # But SwarmAgent classes usually define description in __init__.
            # We'll use a best-effort approach based on class name or docstring.
            
            description = agent_cls.__doc__.strip() if agent_cls.__doc__ else "No description available."
            # If the class has a 'description' attribute (some do), use it.
            if hasattr(agent_cls, "description"):
                description = getattr(agent_cls, "description")

            info = {
                "id": name,
                "name": name.replace("_", " ").title(),
                "description": description,
                "category": "Custom",
                "icon": "Bot",
                "animation_profile": "generic-bot"
            }

            # Map Icons and Animations based on ID conventions
            lower_name = name.lower()
            if "legislation" in lower_name or "legal" in lower_name:
                info["icon"] = "Scale"
                info["animation_profile"] = "document-scanner"
            elif "optimizer" in lower_name or "performance" in lower_name:
                info["icon"] = "Zap"
                info["animation_profile"] = "speedster"
            elif "reasoning" in lower_name or "knowledge" in lower_name:
                info["icon"] = "BrainCircuit"
                info["animation_profile"] = "network-node"
            elif "location" in lower_name or "scout" in lower_name:
                info["icon"] = "MapPin"
                info["animation_profile"] = "map-scan"
            elif "detective" in lower_name: 
                info["icon"] = "Search"
                info["animation_profile"] = "detective"
            elif "janitor" in lower_name: 
                info["icon"] = "Trash2"
                info["animation_profile"] = "sweeper"
            elif "architect" in lower_name: 
                info["icon"] = "LayoutTemplate"
                info["animation_profile"] = "architect"
            elif "analyst" in lower_name: 
                info["icon"] = "TrendingUp"
                info["animation_profile"] = "analyst"
            elif "orchestrator" in lower_name:
                info["icon"] = "Layers"
                info["animation_profile"] = "orchestrator"
            elif "gatekeeper" in lower_name or "security" in lower_name:
                info["icon"] = "ShieldCheck"
                info["animation_profile"] = "shield"

            results.append(info)
            
        return results
