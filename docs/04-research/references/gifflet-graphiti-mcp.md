# Graphiti MCP Server (Gifflet) Analysis

## 1. Synthesis
`gifflet/graphiti-mcp-server` is a specific implementation of an **MCP Server** for the **Graphiti** library (which I analyzed separately). While `getzep-graphiti` is the core library, this repo wraps it into a deployable service compatible with the **Model Context Protocol**.

### Key Differences from Core Library Analysis:
*   **Ready-to-Use Tools**: It explicitly defines the MCP tools:
    *   `add_episode(name, body, group_id, source)`: Adds data.
    *   `search_nodes(query, group_ids, max_nodes)`: Semantic search.
    *   `search_facts(query)`: Searches edges/relationships.
    *   `delete_entity_edge`, `delete_episode`, `clear_graph`.
*   **Infrastructure**: Provides a `docker-compose.yml` that spins up **Neo4j** alongside the MCP server, making it a "one-click" deployable unit.
*   **Custom Entities**: It defines specific Pydantic models for `Requirement`, `Preference`, and `Procedure` to guide the extraction process, tailoring the graph for an "Agent Memory" use case rather than a generic knowledge graph.

### Why this is valuable:
It acts as a **reference implementation** for how to expose the complex Graphiti logic via the simple MCP interface.

## 2. Strategic & Architectural Ideas for Golden Armada

### A. The "Memory Microservice" Pattern
This repo confirms that the Golden Armada's memory should be an **independent service** (MCP Server) rather than a library imported into every agent.
*   **Architecture**:
    *   **Neo4j/SurrealDB**: State store.
    *   **Memory MCP**: Exposes `add_episode`, `search_facts`.
    *   **Agents**: Connect to Memory MCP via stdio or SSE.
*   **Benefit**: Multiple agents (Coder, Planner, Reviewer) can share the *same* memory graph without race conditions or lock contention, as the MCP server manages serialization (using `asyncio.Queue` per `group_id`).

### B. "Group ID" as "Project ID"
The server uses `group_id` to partition the graph.
*   **Golden Armada Mapping**: `group_id` = `repo_name` or `project_id`.
*   **Workflow**: When the "Coding Squad" works on "Project X", they pass `group_id='project-x'` to all memory calls, ensuring they don't hallucinate facts from "Project Y".

### C. The "Entity Ontology" Strategy
The file `graphiti_mcp_server.py` explicitly defines:
```python
class Requirement(BaseModel): ...
class Preference(BaseModel): ...
class Procedure(BaseModel): ...
```
*   **Strategy**: The Golden Armada should define a **Core Ontology** for software engineering:
    *   `Bug` (description, severity, status)
    *   `Feature` (user_story, acceptance_criteria)
    *   `TechDebt` (location, impact)
*   **Implementation**: Passing these definitions to the extraction engine ensures the graph is populated with *useful*, structured nodes, not just random nouns found in the text.

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

To absorb this into our stack:

### Step 1: Deploy the Reference Implementation (with modifications)
We can almost use this repo *as is* for the initial prototype, just swapping the LLM config to use Gemini 1.5 Pro (via OpenAI compatibility mode).
*   **Action**: Fork this repo, add a `GeminiClient` adapter (if not already present in Graphiti core), and deploy it as `memory-mcp`.

### Step 2: Port to SurrealDB (Long Term)
While Neo4j is great, our stack mandates SurrealDB.
*   **Task**: Re-implement `graphiti_mcp_server.py`'s tool logic (`add_episode`, `search_nodes`) to query SurrealDB instead of calling `graphiti_client`.
*   **Schema**: Use the ontology ideas (Requirement, Procedure) to define SurrealDB `DEFINE TABLE` statements.

### Step 3: "Cursor Rules" Adoption
The repo includes `graphiti_cursor_rules.mdc`. This is a set of instructions for the AI on *how* to use the tools.
*   **Integration**: We will copy these rules into the **System Prompt** of our Agno agents.
    *   *Rule*: "Always search first: Use `search_nodes` before starting work."
    *   *Rule*: "Record facts: When a user states a preference, call `add_episode` immediately."

### Summary
This repo fills the gap between "Graphiti the Library" and "Golden Armada the System". It provides the **API Contract** (MCP Tools) and the **Operational Logic** (Queues, Docker) needed to turn the library into a live service. We will adopt its API surface area (`add_episode`, `search_facts`) almost exactly, while swapping the backend for SurrealDB.
