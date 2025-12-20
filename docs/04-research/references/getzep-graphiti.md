# GetZep Graphiti Analysis

## 1. Synthesis: What is Graphiti?
**Graphiti** is a Python framework and MCP server for building **dynamic, temporally-aware Knowledge Graphs** specifically designed for AI Agents. It addresses the limitations of static RAG (Retrieval Augmented Generation) by treating memory as a living, evolving graph rather than a pile of documents.

### Key Differentiators:
1.  **Temporal Awareness**: It solves the "President of the US" problem. If a document from 2016 says "Obama is President" and one from 2017 says "Trump is President", standard RAG might retrieve both or get confused. Graphiti models facts with `valid_at` and `invalid_at` timestamps, allowing "Point-in-Time" queries.
2.  **Episodic Ingestion**: Data is added as "Episodes" (chat logs, events, transactions). The system automatically extracts entities and relationships from these episodes and updates the graph incrementally.
3.  **Hybrid Retrieval**: It doesn't just do vector search. It combines:
    *   **Semantic Search**: Vector embeddings of nodes/edges.
    *   **Keyword Search**: BM25/Full-text search.
    *   **Graph Traversal**: Walking the edges to find related context.
4.  **Edge Invalidation**: It uses an LLM to detect contradictions. If a new fact ("Alice moved to NY") contradicts an old fact ("Alice lives in SF"), it marks the old edge as invalid/expired rather than deleting it, preserving history.

### Tech Stack
*   **Core Logic**: Python (Pydantic for schema).
*   **Storage**: **Neo4j** (Graph + Vector Store).
*   **LLM Integration**: OpenAI/Anthropic for extraction and reasoning.
*   **Interface**: MCP Server and FastAPI.

## 2. Strategic & Architectural Ideas for Golden Armada

### A. The "Memory Service" Backbone
Graphiti validates the hypothesis that **SurrealDB** (a Graph + Vector DB) is the correct choice for the Golden Armada's long-term memory.
*   **Concept**: The Golden Armada shouldn't just dump text into a vector store. It should build a structured graph of the project state.
*   **Application**:
    *   **User**: "Change the button color to blue."
    *   **Graph**: `User` --(REQUESTED)--> `Change(Button, Blue)` --(STATUS)--> `Pending`.
    *   **Later**: "Why is the button blue?" -> Agent queries graph -> "User requested it in Episode #42".

### B. Temporal Edge Management
The `valid_at` / `invalid_at` pattern is crucial for a software engineering agent.
*   **Scenario**: File `utils.py` exports function `helper()`. Later, `utils.py` is refactored and `helper()` is removed.
*   **Graph**: The relationship `utils.py` --(EXPORTS)--> `helper` must be marked invalid, so agents don't try to import it in new code, but still understand old git commits.

### C. Episodic Processing Pipeline
Graphiti's "Ingestion Pipeline" (Extract Nodes -> Deduplicate -> Extract Edges -> Check Contradictions) is a robust pattern for the **Document Ingest Squad**.
*   **Pattern**: Don't just "read" a PDF. Extract the entities (Requirements, Stakeholders, APIs) and link them.

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

To implement Graphiti-like capabilities using our stack:

### Step 1: SurrealDB Schema for Temporal Graphs
We will replicate the Neo4j schema in SurrealDB.
```sql
-- Nodes
DEFINE TABLE entity SCHEMAFULL;
DEFINE FIELD name ON TABLE entity TYPE string;
DEFINE FIELD summary ON TABLE entity TYPE string;
DEFINE FIELD embedding ON TABLE entity TYPE array<float>;
DEFINE INDEX entity_name_vector ON TABLE entity COLUMNS embedding TYPE HNSW ...;

-- Edges (Relationships)
DEFINE TABLE relates_to SCHEMAFULL TYPE RELATION;
DEFINE FIELD fact ON TABLE relates_to TYPE string;
DEFINE FIELD valid_at ON TABLE relates_to TYPE datetime;
DEFINE FIELD invalid_at ON TABLE relates_to TYPE datetime;
-- Graphiti uses 'episodes' list on edges to track source
DEFINE FIELD source_episodes ON TABLE relates_to TYPE array<record<episode>>;
```

### Step 2: The "Memory Squad" (or Service)
Instead of a single library, we implement this as a specialized Squad or MCP Service.
*   **Role**: Listens to the `EventBus` (Chat messages, Git commits).
*   **Action**: "Ingests" the event as an episode.
*   **Tools**:
    *   `extract_entities(text)`: Uses Gemini 1.5 Pro to identify Nodes.
    *   `extract_relations(text, nodes)`: Identifies Edges.
    *   `reconcile_graph(new_edges)`: Queries SurrealDB for conflicting edges and updates `invalid_at`.

### Step 3: Hybrid Search Tool
Create a tool `query_knowledge_graph(query: string)` that performs the "GraphRAG" logic:
1.  **Vector Search**: Find entry point nodes in SurrealDB matching the query embedding.
2.  **Traversal**: Walk `->relates_to->` edges (filtering by `invalid_at == NONE`).
3.  **Context Assembly**: Gather the `fact` properties from the traversed edges.
4.  **Synthesis**: Use LLM to answer the query based on the assembled subgraph.

### Step 4: "Project State" Graph
We will specifically apply this to **Codebase Knowledge**.
*   **Nodes**: `File`, `Class`, `Function`, `Variable`, `Requirement`, `Bug`.
*   **Edges**: `IMPORTS`, `CALLS`, `DEFINES`, `SATISFIES`, `CAUSES`.
*   **Benefit**: When a `Requirement` changes, we can traverse the graph to find all `Functions` that `SATISFY` it and mark them for review.

### Summary
Graphiti provides the **blueprint** for the Golden Armada's memory. We will port its logical patterns (Temporal Edges, Hybrid Search, Episodic Ingestion) from Neo4j/Python to **SurrealDB/Agno**, creating a "Living Memory" that understands the *history* of the project, not just the current snapshot.
