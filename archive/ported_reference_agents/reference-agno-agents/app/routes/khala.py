from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import os
import logging

from khala.infrastructure.surrealdb.client import SurrealDBClient, SurrealConfig
from khala.infrastructure.persistence.surrealdb_repository import SurrealDBMemoryRepository
from khala.interface.mcp.khala_subagent_tools import KHALASubagentTools
from pydantic import SecretStr

router = APIRouter(prefix="/khala", tags=["khala"])
logger = logging.getLogger(__name__)

# Initialize dependencies
SURREAL_URL = os.getenv("SURREALDB_URL", "ws://vivi-surrealdb:8000/rpc")
SURREAL_USER = os.getenv("SURREALDB_USER", "root")
SURREAL_PASS = os.getenv("SURREALDB_PASS", "root")
SURREAL_NS = os.getenv("SURREALDB_NAMESPACE", "vivi")
SURREAL_DB = os.getenv("SURREALDB_DATABASE", "vivi")

# Global instances (lazy initialization recommended but doing eager for now)
db_client = None
khala_tools = None

async def get_khala_tools():
    global db_client, khala_tools
    if khala_tools:
        return khala_tools
    
    try:
        logger.info(f"Initializing Khala Tools with SurrealDB at {SURREAL_URL}")
        config = SurrealConfig(
            url=SURREAL_URL,
            username=SURREAL_USER,
            password=SecretStr(SURREAL_PASS),
            namespace=SURREAL_NS,
            database=SURREAL_DB
        )
        db_client = SurrealDBClient(config=config)
        repository = SurrealDBMemoryRepository(db_client)
        khala_tools = KHALASubagentTools(repository=repository)
        return khala_tools
    except Exception as e:
        logger.error(f"Failed to initialize Khala Tools: {e}")
        raise HTTPException(status_code=500, detail=f"Khala initialization failed: {e}")

@router.get("/search")
async def search_memories(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Limit results")
) -> Dict[str, Any]:
    """Search memories using Khala."""
    tools = await get_khala_tools()
    try:
        # Using default user for now, should extract from auth context
        result = await tools.search_memories(query=q, user_id="default_user", limit=limit)
        return result
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph")
async def get_graph() -> Dict[str, Any]:
    """Get knowledge graph (recent memories)."""
    tools = await get_khala_tools()
    try:
        # Access underlying client to run raw query for recent items
        # This bypasses specific repository filters to give a broad view
        client = tools.repository.client
        
        # Fetch recent 50 memories
        query = "SELECT * FROM memory ORDER BY created_at DESC LIMIT 50;"
        async with client.get_connection() as conn:
            response = await conn.query(query)
            
        memories = []
        if response and isinstance(response, list):
             # Handle SurrealDB response structure [ { result: [...], status: ... } ]
             data = response
             if len(response) > 0 and isinstance(response[0], dict) and 'result' in response[0]:
                 data = response[0]['result']
             
             # Deserialize
             memories = [client._deserialize_memory(m) for m in data]

        # Convert to Graph Format
        nodes = []
        edges = []
        
        for mem in memories:
            # Determine label
            label = "Untitled"
            if mem.tags and len(mem.tags) > 0:
                label = mem.tags[0]
            elif mem.category:
                label = mem.category
            else:
                label = mem.content[:30] + "..." if len(mem.content) > 30 else mem.content

            # Determine type
            node_type = "document"
            if mem.category and mem.category in ["document", "concept", "task", "law"]:
                node_type = mem.category
            elif mem.tags and "task" in mem.tags:
                node_type = "task"
            
            nodes.append({
                "id": mem.id,
                "label": label,
                "type": node_type,
                "properties": {
                    "content": mem.content,
                    "dateAdded": mem.created_at.isoformat(),
                    "importance": mem.importance.value,
                    "tier": mem.tier.value
                }
            })

        return {"nodes": nodes, "edges": edges}

    except Exception as e:
        logger.error(f"Failed to fetch graph: {e}")
        # Return empty graph on error to avoid UI crash
        return {"nodes": [], "edges": []}

from pydantic import BaseModel

class CreateMemoryRequest(BaseModel):
    content: str
    user_id: str = "guest"
    tags: List[str] = []
    category: Optional[str] = None
    metadata: Dict[str, Any] = {}

@router.post("/memory")
async def create_memory(request: CreateMemoryRequest) -> Dict[str, Any]:
    """Create a new memory in Khala."""
    tools = await get_khala_tools()
    try:
        result = await tools.save_memory({
            "content": request.content,
            "user_id": request.user_id,
            "tags": request.tags,
            "category": request.category,
            "metadata": request.metadata
        })
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
            
        return result
    except Exception as e:
        logger.error(f"Failed to create memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
