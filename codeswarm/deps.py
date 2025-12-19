from typing import Generator
from typing import Optional
import logging

from codeswarm.agents.gatekeeper_agent import SecurityAboyeur
from codeswarm.agents.orchestrator_agent import OrchestratorAgent

logger = logging.getLogger(__name__)

# Global instances (simple singleton pattern for now)
_vivi_agent: Optional[SecurityAboyeur] = None
_orchestrator_agent: Optional[OrchestratorAgent] = None

async def get_vivi_agent() -> SecurityAboyeur:
    global _vivi_agent
    if not _vivi_agent:
        logger.info("Initializing Global SecurityAboyeur instance...")
        _vivi_agent = SecurityAboyeur(user_id="default_user")
        await _vivi_agent.initialize()
    return _vivi_agent

async def get_orchestrator_agent() -> OrchestratorAgent:
    global _orchestrator_agent
    if not _orchestrator_agent:
        logger.info("Initializing Global OrchestratorAgent instance...")
        _orchestrator_agent = OrchestratorAgent(user_id="system_orchestrator")
        await _orchestrator_agent.initialize()
    return _orchestrator_agent
