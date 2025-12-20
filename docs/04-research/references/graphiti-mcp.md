# Reference Analysis: Graphiti MCP Server

**Source:** `gitingest-gifflet-graphiti-mcp-server.txt`
**Repo:** gifflet/graphiti-mcp-server (fork/implementation of Graphiti)
**Date:** 2025-03-31

---

## 1. Synthesis: What is the Graphiti MCP Server?

This repository wraps the `graphiti-core` library (which we analyzed in the previous report) into an **MCP (Model Context Protocol)** server. This makes the Graphiti knowledge graph accessible as a standard toolset to any MCP-compliant agent (like Claude Desktop, Cursor, or our own Agno agents if we implement an MCP client).

### Key Components

1.  **FastMCP Implementation**: Uses `mcp.server.fastmcp` to expose tools over SSE (Server-Sent Events) or Stdio.
2.  **Custom Entity Definitions**: Defines specific Pydantic models for `Requirement`, `Preference`, and `Procedure`. This forces the LLM to extract these specific types of knowledge, which is highly relevant to our "Product Manager" and "Dev" agents.
3.  **Episode Queueing**: Implements an `asyncio.Queue` per `group_id` to serialize writes. This prevents race conditions when multiple agents try to write to the same graph context simultaneously.
4.  **Tools Exposed**:
    *   `add_episode`: Ingest text/JSON/messages.
    *   `search_nodes`: Semantic + Graph search for entities.
    *   `search_facts`: Search for relationships.
    *   `delete_episode/entity_edge`: Maintenance.

---

## 2. Strategic Ideas for CodeSwarm (Golden Armada)

This repo provides the **"Interface Layer"** design pattern for our memory system. While `getzep-graphiti` gave us the *core logic*, this repo shows us how to *expose* it to agents effectively.

### A. Strict Schemas for Knowledge
The file `graphiti_mcp_server.py` defines strict classes for:
*   **`Requirement`**: "Project X needs feature Y."
*   **`Preference`**: "User hates dark mode."
*   **`Procedure`**: "Always run tests before commit."

**Strategic Value**: Instead of a generic "Knowledge Graph", we should define a **CodeSwarm Ontology**. Our agents shouldn't just "remember things"; they should remember specific *types* of things that drive software development.

### B. The "Memory Service" Pattern
Instead of embedding the Graph logic directly into every agent (which makes them heavy), we should treat Memory as a **Service** (or a centralized Toolkit).
*   **Current Plan**: `MemoryManagerToolkit` directly in Agno.
*   **Refined Plan**: The Toolkit communicates with a shared SurrealDB instance, but abstracting it via specific *methods* (like `add_requirement`, `get_preferences`) is better than generic "search".

### C. Contextual Cursor Rules
The `graphiti_cursor_rules.mdc` file shows how to prompt an agent to *use* memory effectively:
*   "Always search first."
*   "Capture requirements immediately."
*   "Filter by entity type."

We should bake these rules into our **System Prompts** for the Golden Armada.

---

## 3. Integration Plan (Agno + SurrealDB)

We will incorporate the **Schema-Driven Extraction** and **Tool Interface** ideas from this MCP server into our `MemoryManagerToolkit`.

### Phase 1: Define the CodeSwarm Ontology

In `codeswarm/common/memory/schema.py`:

```python
from pydantic import BaseModel, Field

class Requirement(BaseModel):
    project: str
    description: str
    priority: str

class ArchitectureDecision(BaseModel):
    decision: str
    context: str
    consequences: str

class CodingStandard(BaseModel):
    language: str
    rule: str
    reason: str
```

### Phase 2: Enhanced Memory Toolkit

Update the `MemoryManagerToolkit` to use these specific schemas during ingestion.

**File:** `codeswarm/agno-agents/toolkits/memory_manager.py`

```python
class MemoryManagerToolkit(Toolkit):
    # ... existing init ...

    async def add_memory(self, content: str, type: str = "general"):
        """
        Ingests content. If type is 'requirement', forces the extraction
        LLM to map content to the Requirement schema before saving.
        """
        pass

    async def search_requirements(self, query: str):
        """
        Specialized search that filters for 'Requirement' label nodes
        and returns them structured.
        """
        pass
```

### Phase 3: "Protocol" for Agents

We will add a section to `AGENTS.md` (or a specific `MEMORY_PROTOCOL.md`) dictating how agents must interact with memory, inspired by `graphiti_cursor_rules.mdc`.

*   **Planner**: Must query `search_requirements` before generating a plan.
*   **Developer**: Must query `search_coding_standards` before writing code.
*   **Revisor**: Must query `search_architecture_decisions` when reviewing PRs.

### Phase 4: Async Write Queue (Optional but Good)
The `episode_queues` pattern in `graphiti_mcp_server.py` is smart. Since SurrealDB handles concurrency well, we might not need a strict Python-side queue, but we should ensure our `MemoryManager` is robust against concurrent writes from multiple agents in a Squad.

### Summary
The `graphiti-mcp-server` validates our direction but refines it: **Don't just build a graph; build a Typed Graph tailored to your domain (Software Engineering).**
