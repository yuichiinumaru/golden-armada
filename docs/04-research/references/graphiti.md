# Reference Analysis: Graphiti (Temporal Knowledge Graph)

**Source:** `gitingest-getzep-graphiti.txt`
**Repo:** getzep/graphiti
**Date:** 2025-03-31

---

## 1. Synthesis: What is Graphiti?

Graphiti is a Python framework for building **temporally-aware knowledge graphs**, specifically designed for AI agent memory. Unlike static RAG (Retrieval Augmented Generation) which chunks text into vectors, Graphiti converts unstructured data (chat logs, documents) into a structured Graph of **Entities** and **Relationships** (Edges) that evolves over time.

### Core Concepts

1.  **Bi-Temporal Data Model**:
    *   Every fact (Edge) has a lifecycle.
    *   `valid_at`: When the fact became true in the real world.
    *   `invalid_at`: When the fact ceased to be true (e.g., "User moved from NYC to LA").
    *   `created_at`: When the system learned the fact.
    *   This allows "Point-in-Time" queries (e.g., "Where did the user live last year?").

2.  **Episodic Ingestion**:
    *   Data enters as **Episodes** (Interaction turns, Documents).
    *   An LLM extracts Nodes and Edges from the Episode.
    *   **Deduplication**: New nodes are compared against existing ones (using vector similarity) to prevent duplicates (Entity Resolution).
    *   **Contradiction Analysis**: New facts are compared against existing edges to detect changes in state, invalidating old edges if necessary.

3.  **Hybrid Retrieval**:
    *   Combines **Semantic Search** (Vector Embeddings of Nodes/Edges), **Keyword Search** (BM25), and **Graph Traversal** (Neighbors).
    *   Enables complex reasoning that pure Vector RAG misses (e.g., transitive relationships).

4.  **Tech Stack**:
    *   **Orchestration**: Python (Async).
    *   **Storage**: Neo4j (Graph + Vector Index).
    *   **AI**: OpenAI/Anthropic for Extraction and Reranking.

---

## 2. Strategic Ideas for CodeSwarm (Golden Armada)

Graphiti represents the "Memory Layer" we need for the Golden Armada. Our agents currently lack a structured, evolving view of the project state.

### A. The "Project Knowledge Graph" (PKG)
Instead of just reading files, the Armada should maintain a living graph of the codebase and project goals.
*   **Nodes**: `Feature`, `Bug`, `File`, `Class`, `Function`, `Developer`, `Requirement`.
*   **Edges**: `IMPLEMENTS`, `DEPENDS_ON`, `ASSIGNED_TO`, `BLOCKS`, `FIXES`.
*   **Temporal Aspect**: Crucial for tracking regressions. "Function X worked on Tuesday but broke on Wednesday."

### B. Dynamic Context for Agents
When an agent (e.g., `Planner`) starts a task, instead of dumping all files into the context, it queries the PKG:
*   "Get all `Requirement` nodes related to 'Auth' that are currently `valid`."
*   "Find all `File` nodes that `DEPEND_ON` `user_auth.py`."

### C. Self-Correcting Memory
Graphiti's logic for **Entity Resolution** and **Edge Invalidation** is vital.
*   If a user says "Ignore the previous instruction about AWS, use GCP instead," a standard RAG system might retrieve both.
*   A Graphiti-like system would mark the "Use AWS" edge as `invalid_at: <now>` and create a "Use GCP" edge.

---

## 3. Integration Plan (Agno + SurrealDB)

We will port the *concepts* and *algorithms* of Graphiti to our stack. We will **not** use Neo4j; we will use **SurrealDB**, which supports Graph, Document, and Vector data natively.

### Phase 1: SurrealDB Schema Design

SurrealDB is perfect for this because it allows edges to be distinct records with properties (like `valid_at`).

```sql
-- NODES (Entities)
DEFINE TABLE entity SCHEMAFULL;
DEFINE FIELD name ON TABLE entity TYPE string;
DEFINE FIELD labels ON TABLE entity TYPE array<string>; -- e.g. ["Class", "Python"]
DEFINE FIELD summary ON TABLE entity TYPE string;
DEFINE FIELD embedding ON TABLE entity TYPE array<float>; -- Vector for semantic search
DEFINE INDEX entity_name_vector ON TABLE entity COLUMNS embedding TYPE hnsw DIMENSION 1536 DIST COSINE;

-- EDGES (Relationships)
DEFINE TABLE relation SCHEMAFULL;
DEFINE FIELD in ON TABLE relation TYPE record<entity>;
DEFINE FIELD out ON TABLE relation TYPE record<entity>;
DEFINE FIELD type ON TABLE relation TYPE string; -- e.g. "IMPORTS"
DEFINE FIELD fact ON TABLE relation TYPE string; -- Natural language description
DEFINE FIELD valid_at ON TABLE relation TYPE datetime;
DEFINE FIELD invalid_at ON TABLE relation TYPE datetime; -- Null if currently valid
DEFINE FIELD episode_id ON TABLE relation TYPE record<episode>;
```

### Phase 2: The `MemoryManager` Toolkit

We will implement a Toolkit in Agno that agents use to interact with this graph.

**File:** `codeswarm/agno-agents/toolkits/memory_manager.py`

```python
class MemoryManagerToolkit(Toolkit):
    def __init__(self, db_client):
        # ... setup ...

    async def ingest_episode(self, content: str, source: str):
        """
        1. Summarize content.
        2. Extract Entities & Relations using LLM (Graphiti prompts).
        3. Vectorize Entities.
        4. Entity Resolution (Find similar existing nodes in SurrealDB).
        5. Edge Maintenance (Check for contradictions, invalidate old edges).
        6. Write to DB.
        """
        pass

    async def search_memory(self, query: str):
        """
        1. Embed query.
        2. Vector Search for relevant Entities.
        3. Traverse 1-hop edges from those entities.
        4. Rerank results.
        5. Return structured context.
        """
        pass
```

### Phase 3: Detailed Logic Adaptation (Graphiti -> SurrealDB)

We need to adapt the core algorithms from Graphiti's `graphiti_core` to work with SurrealDB queries.

#### 1. Entity Resolution (Deduplication)
*   **Graphiti**: Uses Neo4j vector index to find candidates, then an LLM to confirm "Are 'UserAuth' and 'AuthService' the same?"
*   **CodeSwarm**: Use SurrealDB's `vector::similarity` function.
    ```sql
    SELECT * FROM entity WHERE vector::similarity(embedding, $new_embedding) > 0.9
    ```
    Then prompt the Revisor Agent (LLM) to confirm the match.

#### 2. Temporal Edge Management
*   **Graphiti**: `get_edge_contradictions` prompt asks LLM if new fact contradicts existing edges.
*   **CodeSwarm**: Implement `invalidate_contradictions` method.
    *   Query existing edges between Source and Target.
    *   Ask LLM: "New fact: 'X is deprecated'. Old fact: 'X is active'. Do these contradict?"
    *   If yes, `UPDATE relation SET invalid_at = time::now() WHERE id = $old_edge_id`.

### Phase 4: The `Librarian` Agent

A specialized agent (part of the "Revisor" or "Admin" squad) responsible for the health of the graph.
*   **Task**: Periodically scan the graph for disconnected nodes, merge duplicate entities that were missed, and summarize dense clusters ("Community Detection" -> "Summary Node").

### Integration Steps

1.  **Dependencies**: Add `surrealdb` driver (already present). No new deps needed.
2.  **Prompts**: Copy and adapt Graphiti's prompts (e.g., `extract_edges.py`, `dedupe_nodes.py`) into `codeswarm/prompts/memory.py`.
3.  **Implementation**: Build the `MemoryManagerToolkit`.
4.  **Testing**: Create a test script that feeds the `AGENTS.md` file as an episode and verifies that Nodes (Admin, Dev) and Edges (Admin -> MANAGES -> Dev) are created correctly.

This moves CodeSwarm from a "Stateless LLM" architecture to a "Stateful Cognitive Architecture."
