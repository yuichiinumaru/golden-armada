# Graphlit: The Knowledge Platform Architecture

## Synthesis
Graphlit is a comprehensive "Knowledge API" platform designed to ingest, process, and retrieve unstructured data for LLM applications. The repository analyzed (`graphlit-mcp-server`) is an implementation of the Model Context Protocol (MCP) that exposes Graphlit's vast capabilities to AI assistants like Cursor or Claude.

At its core, Graphlit acts as a central nervous system for data. It normalizes disparate data sources (Slack, Notion, GitHub, Google Drive, etc.) into a unified "Content" model, applies sophisticated processing workflows (extraction, embedding, summarization), and exposes high-level retrieval and RAG APIs.

**Key Components:**
*   **Feeds:** A powerful abstraction for data connectors. Feeds handle the connection logic, authentication, and scheduling (recurrence) for pulling data from external systems.
*   **Content & Collections:** A unified storage model where everything (a file, a message, a web page) is "Content". Contents can be grouped into "Collections".
*   **Workflows & Specifications:** Declarative configurations that define *how* data is processed. A "Specification" might define the LLM model to use for extraction, while a "Workflow" chains preparation and extraction steps.
*   **Knowledge Graph + Vector Database:** It doesn't just store vectors; it extracts entities and relationships (using LLMs) to build a knowledge graph alongside the vector index.
*   **Multi-Modal Ingestion:** Explicit handling of Audio (transcription), Images (description), and Documents (parsing).

## Strategic Ideas for Golden Armada
Graphlit's architecture offers a blueprint for how "Golden Armada" should handle its internal knowledge base and memory systems.

1.  **The "Feed" Abstraction:** Instead of ad-hoc scripts fetching data, we should formalize "Feeds" as database records in SurrealDB. A Feed record would contain the source type, configuration (repo URL, channel ID), and a `schedule_policy` (e.g., "every 15m").
2.  **Unified Content Schema:** We need a single `content` table in SurrealDB that can store a GitHub Issue, a Discord Message, or a synthesized Research Report with equal ease. This allows for cross-domain search.
3.  **Declarative Processing Pipelines:** Similar to Graphlit's "Workflows", we should store processing instructions in the DB. When new content arrives, a `Processor` agent reads the associated workflow configuration to decide which Gemini 3 model to use for embedding or extraction.
4.  **Short-term vs. Long-term Memory Tools:** Graphlit explicitly distinguishes `ingestMemory` (short-term, transient) from `ingestText` (long-term knowledge). This is a critical pattern for our agents to avoid polluting the permanent knowledge base with scratchpad thinking.
5.  **MCP-First Design:** Graphlit proves the value of exposing the *entire* platform via MCP. We should ensure Golden Armada exposes an MCP server so developers can interact with the agent swarm directly from their IDE.

## Integration Plan (Agno + SurrealDB + Gemini 3)

### 1. SurrealDB Schema Design (The Knowledge Graph)
We will replicate the core entities of Graphlit in SurrealDB:
```sql
DEFINE TABLE feed SCHEMAFULL;
DEFINE FIELD type ON TABLE feed TYPE string; -- 'github', 'discord', 'web'
DEFINE FIELD config ON TABLE feed TYPE object;
DEFINE FIELD schedule_policy ON TABLE feed TYPE object;

DEFINE TABLE content SCHEMAFULL;
DEFINE FIELD type ON TABLE content TYPE string;
DEFINE FIELD body ON TABLE content TYPE string;
DEFINE FIELD embedding ON TABLE content TYPE array<float>;
DEFINE FIELD metadata ON TABLE content TYPE object;
-- Graph relationships
DEFINE TABLE extracted_from SCHEMAFULL TYPE RELATION; -- entity -> extracted_from -> content
```

### 2. The "Librarian Squad" (Agno Team)
Instead of a single "Memory" tool, we create a specialized squad responsible for the integrity of the knowledge base.

*   **`FeedManager` Agent:**
    *   **Role:** Manages the `feed` table.
    *   **Capabilities:** Creates new feeds, checks `schedule_policy`, and dispatches `Ingestor` agents.
    *   **Logic:** Runs a loop (or is triggered by a cron) to find feeds due for updates.

*   **`Ingestor` Agent:**
    *   **Role:** The "hands".
    *   **Capabilities:** Specialized tools for each service (GitHub API, Firecrawl, Discord Bot).
    *   **Task:** Fetches raw data and creates a `content` record with status `processing`.

*   **`Curator` Agent (The Processor):**
    *   **Role:** The "brain".
    *   **Capabilities:** Uses Gemini 3 to process raw content.
    *   **Task:**
        1.  Listens for `content` created events (SurrealDB Live Query).
        2.  Summarizes the content.
        3.  Extracts entities (People, Code, Concepts).
        4.  Generates embeddings (using Gemini's embedding API).
        5.  Updates the `content` record to status `finished`.

### 3. Exposing via MCP
We will build a `golden-armada-mcp` service that wraps the Agno agents.
*   **Tool:** `ask_armada(query)` -> Delegates to a `Research` agent that queries the SurrealDB vector index.
*   **Tool:** `add_knowledge_source(url)` -> Calls `FeedManager` to create a new feed.

### 4. Memory Tiering Implementation
*   **Working Memory:** Implemented as a simple list/buffer in the Agent's context or a temporary Redis/SurrealDB table, cleared after the session.
*   **Long-term Memory:** The `content` table.
*   **Transition:** An agent must explicitly call a tool `save_to_knowledge_base(text, metadata)` to promote a thought from working memory to long-term memory.
