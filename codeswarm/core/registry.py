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
        self.categories: Dict[str, List[str]] = {} # category_name -> [agent_names]
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
            
            # Recursive search for *agent.py files
            # glob.glob with recursive=True requires ** pattern
            search_pattern = os.path.join(abs_dir, "**", "*_agent.py")
            agent_files = glob.glob(search_pattern, recursive=True)
            
            for file_path in agent_files:
                try:
                    self._load_agent_from_file(file_path)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to load agent from {file_path}: {e}")

        logger.info(f"Total agents loaded in registry: {len(self.agents)}")
        logger.info(f"Categories found: {list(self.categories.keys())}")

    def _load_agent_from_file(self, file_path: str):
        """Load a single agent module and register the class."""
        module_name = os.path.basename(file_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Determine category from path
            # Path example: /.../codeswarm/agents/armada/backend/api_agent.py
            # Rel path: agents/armada/backend/api_agent.py
            rel_path = os.path.relpath(file_path, self.base_dir)
            parts = rel_path.split(os.sep)
            
            category = "general"
            if "armada" in parts:
                try:
                    # agents/armada/CATEGORY/agent.py
                    idx = parts.index("armada")
                    if idx + 1 < len(parts) - 1: # ensuring there is a subdir before the filename
                        category = parts[idx + 1]
                except ValueError:
                    pass
            elif "specialists" in parts:
                category = "specialists"
            
            # Find SwarmAgent subclasses
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if (isinstance(attribute, type) and 
                    issubclass(attribute, SwarmAgent) and 
                    attribute is not SwarmAgent):
                    
                    # Register Agent
                    self.agents[attribute_name] = attribute
                    
                    # Register Category
                    if category not in self.categories:
                        self.categories[category] = []
                    self.categories[category].append(attribute_name)
                    
                    logger.debug(f"Registered agent: {attribute_name} in category: {category}")

    def get_agent(self, agent_name: str, user_id: str = "default") -> Optional[SwarmAgent]:
        """Instantiate and get an agent by class name."""
        agent_class = self.agents.get(agent_name)
        if agent_class:
            return agent_class(user_id=user_id)
        return None

    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self.agents.keys())
        
    def get_categories(self) -> List[str]:
        """List all discovered categories."""
        return list(self.categories.keys())
        
    def get_agents_by_category(self, category: str) -> List[str]:
        """Get list of agent names in a specific category."""
        return self.categories.get(category, [])

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
                
            # Find category for this agent
            agent_category = "Custom"
            for cat, agents in self.categories.items():
                if name in agents:
                    agent_category = cat.title()
                    break

            info = {
                "id": name,
                "name": name.replace("_", " ").title(),
                "description": description,
                "category": agent_category,
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
