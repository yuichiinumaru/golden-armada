import asyncio
import os
import logging
from typing import Optional, List, Dict, Any

from agno.agent import Agent
from agno.models.google import Gemini
# from agno.models.openai import OpenAIChat # Uncomment if needed

# Configure logging
logger = logging.getLogger(__name__)

from app.lib.khala_client import KhalaClient
from app.lib.api_keys import get_api_key

# Robust import for Khala Entities
try:
    from khala.domain.memory.entities import Memory, MemoryTier, ImportanceScore
except ImportError:
    # We don't need to define mocks here if KhalaClient handles it internally,
    # but type hinting might need them.
    Memory = Any
    MemoryTier = Any
    ImportanceScore = Any

# Get credentials from environment or raise error
SURREALDB_URL = os.getenv("SURREALDB_URL", "ws://surrealdb:8000/rpc")
SURREALDB_USER = os.getenv("SURREALDB_USER", "root")
SURREALDB_PASS = os.getenv("SURREALDB_PASS", "root")

if SURREALDB_USER == "root" and SURREALDB_PASS == "root":
    logger.warning("Using default root/root credentials for SurrealDB. This is not recommended for production.")

class KhalaBaseAgent:
    """
    Base class for agents using Khala Memory System.
    """
    def __init__(
        self, 
        user_id: str, 
        agent_name: str,
        model_id: str = "gemini-2.5-flash",
        tools: List[Any] = None,
        system_prompt: str = "You are a helpful assistant."
    ):
        self.user_id = user_id
        self.agent_name = agent_name
        self._khala = None
        
        # Initialize Agno Agent
        self.agent = Agent(
            name=agent_name,
            description=system_prompt,
            instructions=system_prompt,
            tools=tools or [],
            model=Gemini(id=model_id, api_key=os.getenv("GOOGLE_API_KEY")),
            # We manage memory manually via Khala, so we might not use Agno's built-in memory
            # or we can sync them. For now, we keep Agno memory disabled or default.
        )

    @property
    def khala(self) -> KhalaClient:
        """Lazy load Khala client if not initialized."""
        if not hasattr(self, '_khala') or self._khala is None:
            self._khala = KhalaClient()
        return self._khala

    async def initialize(self):
        """Connect to database."""
        try:
            await self.khala.initialize()
            logger.info(f"[{self.agent_name}] Connected to Khala Memory.")
        except Exception as e:
            logger.error(f"[{self.agent_name}] Failed to connect to Khala: {e}")
            # Do not raise here, allow agent to function without memory
            # raise

    async def remember(self, content: str, importance: float = 0.5, tags: List[str] = None, user_id: str = None):
        """Store a memory in Khala."""
        target_user = user_id or self.user_id
        try:
            memory_id = await self.khala.create_memory(
                content=content,
                user_id=target_user,
                agent_id=self.agent_name,
                tags=tags or [],
                metadata={"importance": importance}
            )
            logger.debug(f"[{self.agent_name}] Stored memory: {memory_id}")
            return memory_id
        except Exception as e:
            logger.warning(f"[{self.agent_name}] Failed to remember: {e}")
            return None

    async def recall(self, query: str, top_k: int = 5, user_id: str = None) -> List[str]:
        """Recall memories using Khala."""
        target_user = user_id or self.user_id
        try:
            results = await self.khala.search(
                query=query,
                user_id=target_user,
                top_k=top_k
            )
            return [r['content'] for r in results]
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
        
        # 3. Generate response
        # Agno's run() returns a RunResponse object
        # Run in executor to avoid blocking async loop
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: self.agent.run(full_prompt))
        
        # Extract steps/thoughts from response if available
        # This depends on Agno's internal structure. 
        # For now, we'll try to extract tool calls from the agent's memory or response messages
        steps = []
        if hasattr(response, 'messages'):
            for msg in response.messages:
                if msg.role == 'tool':
                    steps.append(f"Tool Result: {msg.content[:50]}...")
                elif msg.role == 'assistant' and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        steps.append(f"Executing: {tool_call.function.name}")
        
        # 4. Store the interaction
        await self.remember(f"User: {message}\nAssistant: {response.content}", importance=0.3, tags=["chat_interaction"], user_id=target_user)
        
        return {
            "response": response.content,
            "steps": steps
        }

    async def close(self):
        await self.khala.close()
