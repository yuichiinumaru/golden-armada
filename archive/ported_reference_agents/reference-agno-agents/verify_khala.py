
import asyncio
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env vars
load_dotenv()

async def verify_connection():
    try:
        from khala.infrastructure.surrealdb.client import SurrealDBClient
        
        url = os.getenv("SURREALDB_URL")
        user = os.getenv("SURREALDB_USER")
        password = os.getenv("SURREALDB_PASS")
        
        logger.info(f"Connecting to SurrealDB at {url} as {user}...")
        
        client = SurrealDBClient(url=url, username=user, password=password)
        await client.initialize()
        
        logger.info("✅ Successfully connected to SurrealDB via Khala!")
        await client.close()
        return True
        
    except ImportError:
        logger.error("❌ Failed to import Khala. Is it installed?")
        return False
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_connection())
    if not success:
        exit(1)
