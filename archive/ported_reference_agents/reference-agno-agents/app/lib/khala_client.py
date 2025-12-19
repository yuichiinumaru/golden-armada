import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# robust import strategy for Khala
try:
    from khala.infrastructure.surrealdb.client import SurrealDBClient, SurrealConfig
    from khala.domain.memory.entities import Memory, MemoryTier, ImportanceScore
    KHALA_AVAILABLE = True
except ImportError:
    logger.warning("Khala library not found. Using internal mock implementations.")
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
    Wraps the SurrealDBClient and handles configuration from environment variables.
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
            
        # Check explicit disable or fallback if library is missing
        env_val = os.getenv("ENABLE_KHALA", "true")
        self.enabled = (env_val.lower() == "true") and KHALA_AVAILABLE
        
        if not self.enabled:
            reason = "Disabled via env" if env_val.lower() == "false" else "Library missing"
            logger.info(f"Khala Memory System disabled ({reason}). Using mock implementation.")
            self._initialized = True
            return

        self.url = os.getenv("SURREALDB_URL", "ws://vivi-surrealdb:8000/rpc")
        self.user = os.getenv("SURREALDB_USER", "root")
        self.password = os.getenv("SURREALDB_PASS", "root")
        self.namespace = os.getenv("SURREALDB_NAMESPACE", "khala")
        self.database = os.getenv("SURREALDB_DATABASE", "memory")
        
        try:
            # We use the imported classes (real or mock)
            # If KHALA_AVAILABLE is True, we try to use them properly
            from pydantic import SecretStr

            config = SurrealConfig(
                url=self.url,
                username=self.user,
                password=SecretStr(self.password) if KHALA_AVAILABLE else self.password,
                namespace=self.namespace,
                database=self.database
            )
            self.db_client = SurrealDBClient(config=config)
            logger.info(f"KhalaClient initialized for {self.url} ({self.namespace}/{self.database})")
        except Exception as e:
            logger.error(f"Failed to initialize KhalaClient: {e}")
            self.enabled = False

        self._initialized = True

    async def initialize(self):
        """Initialize the database client."""
        if not self.enabled:
            return
        await self.db_client.initialize()

    async def connect(self):
        """Connect to the database."""
        if not self.enabled:
            return
        await self.db_client.initialize()

    async def close(self):
        """Close the database connection."""
        if not self.enabled:
            return
        await self.db_client.close()

    async def create_memory(self, content: str, user_id: str, agent_id: str, tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Create a new memory."""
        if not self.enabled:
            logger.debug(f"[MOCK] Created memory for {user_id}: {content[:50]}...")
            return "mock_memory_id"

        # Agent ID is now part of metadata or source, not a core field
        final_metadata = metadata or {}
        final_metadata["agent_id"] = agent_id
        
        # Use the imported Memory class (real or mock)
        if KHALA_AVAILABLE:
            memory = Memory(
                content=content,
                user_id=user_id,
                tier=MemoryTier.SHORT_TERM, # Default tier
                importance=ImportanceScore.medium(), # Default importance
                tags=tags or [],
                metadata=final_metadata
            )
            return await self.db_client.create_memory(memory)
        else:
            return "mock_memory_id"

    async def search(self, query: str, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search memories."""
        if not self.enabled:
            logger.debug(f"[MOCK] Searching memories for {user_id}: {query}")
            return []

        if KHALA_AVAILABLE:
            results = await self.db_client.search_memories_by_bm25(
                query_text=query,
                user_id=user_id,
                top_k=top_k
            )
            return results
        return []

    async def get_graph(self, limit: int = 50) -> Dict[str, Any]:
        """Get the memory graph (nodes and edges)."""
        if not self.enabled:
            return {"nodes": [], "edges": []}

        # Placeholder for graph retrieval logic
        return {"nodes": [], "edges": []}

    async def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """
        Ingest a document by sending it to the Marker service for conversion.
        """
        marker_url = os.getenv("MARKER_API_URL", "http://10.5.90.98:8002/api/v1")
        import requests
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                # Timeout is important to avoid hanging
                response = requests.post(f"{marker_url}/convert", files=files, timeout=30)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to ingest document {file_path}: {e}")
            return {"status": "error", "error": str(e)}
