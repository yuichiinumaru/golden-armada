import os
import logging
from typing import Optional, List, Dict, Any

from codeswarm.config import (
    SURREAL_URL,
    SURREAL_USER,
    SURREAL_PASS,
    SURREAL_NS,
    SURREAL_DB
)

logger = logging.getLogger(__name__)

# robust import strategy for Khala
try:
    from khala.infrastructure.surrealdb.client import SurrealDBClient, SurrealConfig
    from khala.domain.memory.entities import Memory, MemoryTier, ImportanceScore
    KHALA_AVAILABLE = True
except ImportError:
    # logger.warning("Khala library not found. Using internal mock implementations.") 
    # Suppress warning if not actively needed, but keeping for debug.
    KHALA_AVAILABLE = False

    # Mock Classes
    class SurrealConfig:
        def __init__(self, **kwargs): pass

    class SurrealDBClient:
        def __init__(self, config=None, **kwargs): self.client = None
        async def initialize(self): pass
        async def close(self): pass
        async def create_memory(self, memory) -> str: return "mock_memory_id"
        async def search_memories_by_bm25(self, query_text, user_id, top_k) -> List[Dict]: return []

    class Memory:
        def __init__(self, **kwargs): pass

    class MemoryTier:
        SHORT_TERM = "short_term"

    class ImportanceScore:
        @staticmethod
        def medium(): return 0.5

class KhalaClient:
    """
    Centralized client for interacting with the Khala Memory System.
    Wraps the SurrealDBClient and handles configuration for Codeswarm.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KhalaClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.config = SurrealConfig(
            url=SURREAL_URL,
            username=SURREAL_USER,
            password=SURREAL_PASS,
            namespace=SURREAL_NS,
            database=SURREAL_DB
        )
        self.db_client = SurrealDBClient(self.config)
        self._initialized = True

    async def initialize(self):
        """Async initialization of the connection."""
        await self.db_client.initialize()
        if KHALA_AVAILABLE:
            logger.info(f"✅ Khala Client initialized (URL: {SURREAL_URL})")
        else:
            logger.warning("⚠️ Khala Client initialized in MOCK mode")

    async def close(self):
        """Close connection."""
        await self.db_client.close()

    async def create_memory(self, content: str, user_id: str, tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Create a generic memory entry."""
        final_metadata = metadata or {}
        final_metadata.update({"source": "codeswarm_agent"})
        
        if KHALA_AVAILABLE:
            memory = Memory(
                content=content,
                user_id=user_id,
                tier=MemoryTier.SHORT_TERM,
                importance=ImportanceScore.medium(),
                tags=tags or [],
                metadata=final_metadata
            )
            return await self.db_client.create_memory(memory)
        else:
            return "mock_memory_id"

    async def search_memories(self, query: str, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search memories using BM25 or generic search."""
        if KHALA_AVAILABLE:
            results = await self.db_client.search_memories_by_bm25(
                query_text=query,
                user_id=user_id,
                top_k=top_k
            )
            return results
        return []
