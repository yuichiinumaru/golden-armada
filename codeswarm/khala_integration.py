import asyncio
import logging
import os
import threading
from typing import Optional, List, Any, Dict

# Khala imports
try:
    from khala.infrastructure.surrealdb.client import SurrealDBClient, SurrealConfig
    from khala.infrastructure.cache.cache_manager import CacheManager
    KHALA_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Khala integration disabled due to import error: {e}")
    KHALA_AVAILABLE = False

from . import config

logger = logging.getLogger(__name__)

# --- Background Loop Management ---
_loop = None
_loop_thread = None

def _start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def run_khala_coro(coro):
    global _loop
    if _loop is None:
        raise RuntimeError("Khala system not started")
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result()

# --- System Definition ---

class KhalaSystem:
    _instance = None

    def __init__(self):
        if not KHALA_AVAILABLE:
            return

        # Configure SurrealDB
        os.environ.setdefault("SURREAL_URL", config.SURREAL_URL)
        os.environ.setdefault("SURREAL_NS", config.SURREAL_NS)
        os.environ.setdefault("SURREAL_DB", config.SURREAL_DB)
        os.environ.setdefault("SURREAL_USER", config.SURREAL_USER)
        os.environ.setdefault("SURREAL_PASS", config.SURREAL_PASS)

        self.surreal_client = SurrealDBClient()
        self.cache_manager = CacheManager()
        self.started = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = KhalaSystem()
        return cls._instance

    async def start(self):
        if not KHALA_AVAILABLE or self.started:
            return

        try:
            logger.info("Starting Khala Memory System...")
            await self.surreal_client.initialize()
            await self.cache_manager.start()
            self.started = True
            logger.info("Khala Memory System Started.")
        except Exception as e:
            logger.error(f"Failed to start Khala System: {e}")

    async def stop(self):
        if not KHALA_AVAILABLE or not self.started:
            return

        logger.info("Stopping Khala Memory System...")
        await self.cache_manager.stop()
        await self.surreal_client.close()
        self.started = False

    async def search(self, query: str, user_id: str = "codeswarm") -> str:
        # Use BM25 search from SurrealDBClient
        try:
            results = await self.surreal_client.search_memories_by_bm25(query, user_id, top_k=5)
            if not results:
                return "No relevant memories found."

            # Format results
            formatted = []
            for res in results:
                formatted.append(f"- {res.get('content', '')}")
            return "\n".join(formatted)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Error searching memories: {e}"

# --- Tools ---

def khala_search_tool(query: str) -> str:
    """Search the Khala memory base for relevant information."""
    sys = KhalaSystem.get_instance()
    if not sys:
        return "Memory system unavailable."

    try:
        return run_khala_coro(sys.search(query))
    except Exception as e:
        return f"Search failed: {e}"

# --- Lifecycle Helpers ---

def start_khala_background():
    global _loop, _loop_thread
    if not KHALA_AVAILABLE:
        return

    if _loop is not None:
        return

    _loop = asyncio.new_event_loop()
    _loop_thread = threading.Thread(target=_start_loop, args=(_loop,), daemon=True)
    _loop_thread.start()

    sys = KhalaSystem.get_instance()
    future = asyncio.run_coroutine_threadsafe(sys.start(), _loop)
    try:
        future.result(timeout=10)
    except Exception as e:
        logger.error(f"Khala start failed: {e}")

def stop_khala_background():
    global _loop
    if _loop:
        sys = KhalaSystem.get_instance()
        future = asyncio.run_coroutine_threadsafe(sys.stop(), _loop)
        try:
             future.result(timeout=5)
        except:
             pass
        _loop.call_soon_threadsafe(_loop.stop)
        _loop = None

def get_khala_tools() -> List[Any]:
    if not KHALA_AVAILABLE:
        return []
    return [khala_search_tool]
