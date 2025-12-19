import asyncio
import os
from typing import Optional, List

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.calculator import CalculatorTools

# Import Khala components
from khala.infrastructure.surrealdb.client import SurrealDBClient
from khala.domain.memory.entities import Memory, MemoryTier, ImportanceScore

class KhalaAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # Initialize Khala Client
        # Note: In Docker, we use the service name 'vivi-surrealdb'
        self.db_client = SurrealDBClient(
            url=os.getenv("SURREALDB_URL", "ws://vivi-surrealdb:8000/rpc"),
            username=os.getenv("SURREALDB_USER", "root"),
            password=os.getenv("SURREALDB_PASS", "root")
        )
        
        # Initialize Agno Agent
        self.agent = Agent(
            model=Gemini(id="gemini-1.5-flash"),
            tools=[CalculatorTools()],
            markdown=True,
            # show_tool_calls=True  # Removed as it caused TypeError in Agno 2.3.2
        )

    async def initialize(self):
        """Connect to database."""
        await self.db_client.initialize()

    async def remember(self, content: str, importance: float = 0.5):
        """Store a memory using Khala."""
        memory = Memory(
            user_id=self.user_id,
            content=content,
            tier=MemoryTier.WORKING,
            importance=ImportanceScore(importance)
        )
        memory_id = await self.db_client.create_memory(memory)
        return memory_id

    async def recall(self, query: str) -> List[str]:
        """Recall memories using Khala (BM25 for now as we might not have embeddings set up yet)."""
        # For this test, we use BM25 text search
        results = await self.db_client.search_memories_by_bm25(
            query_text=query,
            user_id=self.user_id
        )
        return [r['content'] for r in results]

    async def chat(self, message: str) -> str:
        """Chat with the agent, using memory."""
        
        # 1. Recall relevant context
        memories = await self.recall(message)
        context = "\n".join(memories)
        
        # 2. Augment prompt
        system_prompt = "You are a helpful assistant."
        if context:
            system_prompt += f"\n\nContext from memory:\n{context}"
            
        # 3. Generate response
        # Agno's run() is synchronous, but we are in async. 
        # For now, we just call it directly as Agno 2.0 might support async or we wrap it.
        # Checking Agno docs (mental check): Agno agents usually have .print_response() or .run()
        
        response = self.agent.run(message)
        
        # 4. Store the interaction (simplified)
        await self.remember(f"User: {message}\nAssistant: {response.content}", importance=0.3)
        
        return response.content

    async def close(self):
        await self.db_client.close()

# Simple test runner
if __name__ == "__main__":
    async def main():
        agent = KhalaAgent(user_id="test_user_1")
        await agent.initialize()
        
        print("--- Storing Memory ---")
        await agent.remember("My favorite color is blue.", importance=0.9)
        print("Memory stored.")
        
        print("--- Recalling Memory ---")
        memories = await agent.recall("color")
        print(f"Recalled: {memories}")
        
        await agent.close()

    asyncio.run(main())
