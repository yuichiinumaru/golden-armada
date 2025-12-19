from typing import Dict, Any, Optional, List, Type
import logging
import pkgutil
import importlib
import app.agents
from app.templates.base_agent import KhalaBaseAgent

from app.agents.security_aboyeur import SecurityAboyeur
from app.agents.legal_advisor import LegalAdvisorAgent
from app.agents.performance_optimizer import PerformanceOptimizerAgent
from app.agents.knowledge_synthesizer import KnowledgeSynthesizerAgent
from app.agents.location_scout import LocationScoutAgent
from app.agents.bi_detective import BIDetectiveAgent
from app.agents.bi_janitor import BIJanitorAgent
from app.agents.bi_architect import BIArchitectAgent
from app.agents.bi_analyst import BIAnalystAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    def __init__(self):
        self.vivi_agent: Optional[SecurityAboyeur] = None
        self.other_agents: Dict[str, Any] = {}
        self._is_initialized = False

    async def initialize(self):
        if self._is_initialized:
            return

        logger.info("Initializing Agent Registry...")

        # Initialize Security Aboyeur (formerly Vivi)
        self.vivi_agent = SecurityAboyeur(user_id="default_user") # TODO: Dynamic user_id
        await self.vivi_agent.initialize()

        # Initialize mapped agents (Legacy)
        self.other_agents["legislation-ingestor"] = await self._init_agent(LegalAdvisorAgent, "setup_agent")
        self.other_agents["apex-optimizer"] = await self._init_agent(PerformanceOptimizerAgent, "setup_agent")
        self.other_agents["deep-reasoner"] = await self._init_agent(KnowledgeSynthesizerAgent, "setup_agent")
        self.other_agents["location-scout"] = await self._init_agent(LocationScoutAgent, "setup_agent")

        # Alias for gemini-3-pro-preview (maps to Apex Optimizer)
        self.other_agents["gemini-3-pro-preview"] = self.other_agents["apex-optimizer"]

        self.other_agents["mastra-agent"] = self.vivi_agent

        # Initialize BI Squad (Modern - Manual load for safety)
        self.other_agents["bi-detective"] = await self._init_agent(BIDetectiveAgent, "initialize")
        self.other_agents["bi-janitor"] = await self._init_agent(BIJanitorAgent, "initialize")
        self.other_agents["bi-architect"] = await self._init_agent(BIArchitectAgent, "initialize")
        self.other_agents["bi-analyst"] = await self._init_agent(BIAnalystAgent, "initialize")

        # Dynamic Scan for NEW agents
        await self._scan_dynamic_agents()

        self._is_initialized = True
        logger.info(f"Agent Registry initialized with {len(self.other_agents)} mapped agents.")

    async def _scan_dynamic_agents(self):
        """Scans app.agents for new KhalaBaseAgent subclasses."""
        package = app.agents
        prefix = package.__name__ + "."

        for _, name, _ in pkgutil.iter_modules(package.__path__, prefix):
            # Skip known manually loaded or internal modules
            short_name = name.split(".")[-1]
            if short_name in ["registry", "test_agent", "poet", "orchestrator", "security_aboyeur",
                              "legal_advisor", "performance_optimizer", "knowledge_synthesizer", "location_scout",
                              "bi_detective", "bi_janitor", "bi_architect", "bi_analyst"]:
                continue

            try:
                module = importlib.import_module(name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, KhalaBaseAgent) and
                        attr is not KhalaBaseAgent and
                        attr.__module__ == module.__name__):

                        # Generate ID: MyNewAgent -> my-new-agent or just module name
                        agent_id = short_name.replace("_", "-")

                        if agent_id not in self.other_agents:
                            logger.info(f"Dynamically loaded agent: {agent_id}")
                            self.other_agents[agent_id] = await self._init_agent(attr, "initialize")
            except Exception as e:
                logger.warning(f"Failed to dynamic scan {name}: {e}")

    async def _init_agent(self, agent_cls: Type, method_name: str) -> Any:
        try:
            # Check if constructor accepts user_id (KhalaBaseAgent does)
            try:
                agent = agent_cls(user_id="system")
            except TypeError:
                agent = agent_cls()

            if hasattr(agent, method_name):
                init_func = getattr(agent, method_name)
                if callable(init_func):
                    await init_func()
            return agent
        except Exception as e:
            logger.error(f"Failed to initialize agent {agent_cls.__name__}: {e}")
            return None

    async def shutdown(self):
        if self.vivi_agent:
            await self.vivi_agent.close()
        self._is_initialized = False
        logger.info("Agent Registry shutdown.")

    def get_vivi_agent(self) -> Optional[SecurityAboyeur]:
        return self.vivi_agent

    def get_agent(self, agent_id: str) -> Any:
        if agent_id in ["vivi", "vivi-generalist", "default", "gemini-2.5-flash", "gemini-pro"]:
            return self.vivi_agent
        return self.other_agents.get(agent_id)

    def get_mapped_agents_ids(self) -> List[str]:
        return list(self.other_agents.keys())

    def list_agents(self) -> List[str]:
        """Alias for get_mapped_agents_ids to match interface."""
        agents = self.get_mapped_agents_ids()
        if "vivi" not in agents:
            agents.append("vivi")
        return agents

    def get_agents_info(self) -> List[Dict[str, Any]]:
        """Returns detailed info for all agents."""
        results = []
        # Add Vivi
        if self.vivi_agent:
            results.append({
                "id": "vivi",
                "name": self.vivi_agent.agent_name,
                "description": "Security Aboyeur & Router",
                "category": "Core",
                "icon": "ShieldCheck"
            })

        for aid, agent in self.other_agents.items():
            if aid == "mastra-agent" or aid == "gemini-3-pro-preview": continue

            info = {
                "id": aid,
                "name": getattr(agent, "agent_name", aid.title()),
                "description": getattr(agent, "description", "No description available."),
                "category": "Custom",
                "icon": "Bot"
            }

            # Try to extract description from Agno agent
            if hasattr(agent, "agent") and hasattr(agent.agent, "description"):
                 info["description"] = agent.agent.description

            # Legacy Overrides
            if aid == "legislation-ingestor":
                info["name"] = "Legal Advisor"
                info["icon"] = "Scale"
                info["animation_profile"] = "document-scanner"
            elif aid == "apex-optimizer":
                info["name"] = "Performance Optimizer"
                info["icon"] = "Zap"
                info["animation_profile"] = "speedster"
            elif aid == "deep-reasoner":
                info["name"] = "Knowledge Synthesizer"
                info["icon"] = "BrainCircuit"
                info["animation_profile"] = "network-node"
            elif aid == "location-scout":
                info["name"] = "Location Scout"
                info["icon"] = "MapPin"
                info["animation_profile"] = "map-scan"
            elif "detective" in aid: 
                info["icon"] = "Search"
                info["animation_profile"] = "detective"
            elif "janitor" in aid: 
                info["icon"] = "Trash2"
                info["animation_profile"] = "sweeper"
            elif "architect" in aid: 
                info["icon"] = "LayoutTemplate"
                info["animation_profile"] = "architect"
            elif "analyst" in aid: 
                info["icon"] = "TrendingUp"
                info["animation_profile"] = "analyst"
            else:
                info["animation_profile"] = "generic-bot"

            results.append(info)
        return results
