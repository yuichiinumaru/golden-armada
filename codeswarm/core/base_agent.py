import asyncio
import os
import logging
from typing import Optional, List, Dict, Any

from agno.agent import Agent
from agno.models.google import Gemini

# Configure logging
logger = logging.getLogger(__name__)

from codeswarm.core.khala_client import KhalaClient
from codeswarm.core.api_keys import get_api_key

class SwarmAgent:
    """
    Base class for Codeswarm agents, providing integrated Khala Memory capabilities.
    Wraps the standard Agno Agent.
    """
    def __init__(
        self, 
        user_id: str, 
        agent_name: str,
        role: str = "Assistant",
        model_id: str = "gemini-2.5-flash",
        tools: List[Any] = None,
        instructions: str = "You are a helpful assistant.",
        use_memory: bool = True
    ):
        self.user_id = user_id
        self.agent_name = agent_name
        self._khala = None
        self.use_memory = use_memory
        self.tools = tools or []
        self.model_id = model_id
        self.system_prompt = instructions # Storing for potential lazy init or re-init
        self.instructions = instructions # Storing for potential lazy init or re-init
        self.role = role # Storing for potential lazy init or re-init
        
        # Initialize Agno Agent
        # Note: We use instructions as the system prompt
        # Get API key using rotation system
        api_key = get_api_key()
        
        self.agent = Agent(
            name=self.agent_name,
            role=self.role,
            description=self.system_prompt,
            instructions=self.instructions,
            tools=self.tools,
            model=Gemini(id=self.model_id, api_key=api_key),
            markdown=True
        )
    
    @property
    def khala(self) -> KhalaClient:
        if not self.use_memory:
            raise RuntimeError(f"Agent {self.agent_name} has memory disabled.")
        if self._khala is None:
            self._khala = KhalaClient()
        return self._khala

    async def setup_agent(self):
        """Initialize resources (Khala connection)."""
        if self.use_memory:
            await self.khala.initialize()

    async def remember(self, content: str, importance: float = 0.5, tags: List[str] = None, user_id: str = None):
        """Store an interaction or insight in memory."""
        if not self.use_memory:
            return

        target_user = user_id or self.user_id
        try:
            await self.khala.create_memory(
                content=content,
                user_id=target_user,
                tags=tags or [self.agent_name],
                metadata={"agent_name": self.agent_name, "importance": importance}
            )
            logger.debug(f"[{self.agent_name}] Stored memory.")
        except Exception as e:
            logger.warning(f"[{self.agent_name}] Failed to remember: {e}")

    async def recall(self, query: str, top_k: int = 3, user_id: str = None) -> List[str]:
        """Retrieve relevant context from memory."""
        if not self.use_memory:
            return []

        target_user = user_id or self.user_id
        try:
            results = await self.khala.search_memories(
                query=query,
                user_id=target_user,
                top_k=top_k
            )
            # Assuming search_memories returns list of dicts with 'content'
            return [r.get('content', '') for r in results if r.get('content')]
        except Exception as e:
            logger.warning(f"[{self.agent_name}] Failed to recall: {e}")
            return []

    async def chat(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Chat with the agent, using memory."""
        target_user = user_id or self.user_id
        
        # 1. Recall relevant context
        memories = await self.recall(message, user_id=target_user)
        context = "\n".join(memories)
        
        full_prompt = message
        if context:
            full_prompt = f"Context from memory:\n{context}\n\nUser: {message}"
            
        logger.info(f"[{self.agent_name}] Processing message: {message}")
        
        # 3. Generate response using Agno run method
        # We wrap the synchronous run call in a thread executor
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: self.agent.run(full_prompt))
        
        # 4. Store the interaction
        await self.remember(f"User: {message}\nAssistant: {response.content}", importance=0.3, tags=["chat_interaction"], user_id=target_user)
        
        return {
            "response": response.content,
            "full_object": response
        }

    async def run_task(self, task_description: str) -> Dict[str, Any]:
        """Execute a specific task."""
        return await self.chat(task_description)

    async def close(self):
        if self.use_memory and self._khala:
            await self.khala.close()
