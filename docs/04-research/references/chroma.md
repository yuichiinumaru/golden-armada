# Chroma MCP Server: Vector Search Pattern

## Synthesis
The `privetin-chroma` repository is a Python-based implementation of an MCP server that wraps ChromaDB, a popular open-source vector database. It provides a standardized interface for AI agents to interact with a semantic search engine.

**Key capabilities:**
*   **CRUD Operations:** Full lifecycle management of documents (create, read, update, delete).
*   **Semantic Search:** Uses `sentence-transformers` (specifically `all-MiniLM-L6-v2`) to generate embeddings locally and allows querying by semantic similarity.
*   **Metadata Filtering:** Enables precise retrieval by combining vector search with structured metadata filters (e.g., "find documents about 'agents' where `year=2024`").
*   **Robustness:** Implements a custom `@retry_operation` decorator with exponential backoff to handle transient database errors.

## Strategic Ideas for Golden Armada
While Golden Armada uses **SurrealDB** as its primary data store, this Chroma implementation provides a perfect reference implementation for how to expose **Vector Search** capabilities via MCP.

1.  **The "Vector Store" Interface:** The tools defined here (`create_document`, `search_similar`) represent the atomic operations any "Memory" or "Knowledge" agent needs. We should mirror this API surface in our own system.
2.  **Metadata-Aware Search:** The ability to filter by metadata *during* a vector search is critical. SurrealDB supports this natively (filtering on fields while sorting by vector distance). We must ensure our search tools expose this capability to the agents.
3.  **Error Handling Patterns:** The explicit mapping of database errors (like "Document not found") to user-friendly messages is essential for agent reliability. If an agent tries to delete a non-existent document, it should get a clear signal rather than a stack trace.
4.  **Local vs. Remote Embeddings:** This repo uses local embedding generation. In Golden Armada, we delegate this to **Gemini 3**. We must ensure our "Ingestion" agents handle the async nature of calling the Gemini API for embeddings before inserting into SurrealDB.

## Integration Plan (Agno + SurrealDB + Gemini 3)

### 1. Replicating the Interface with SurrealDB
We will implement an MCP server (or a set of Agno tools) that mimics the Chroma capabilities but is backed by SurrealDB.

**SurrealDB Vector Schema:**
```sql
-- Enable vector indexing on the 'embedding' field
DEFINE INDEX vector_idx ON TABLE content COLUMNS embedding TYPE HNSW DIMENSION 768 DIST COSINE;
```

**Tool Mapping:**

| Chroma Tool | Golden Armada Tool | Implementation Logic |
| :--- | :--- | :--- |
| `create_document` | `save_memory` | 1. Call Gemini 3 to get embedding for `content`<br>2. `CREATE content SET body=$content, embedding=$emb, metadata=$meta` |
| `search_similar` | `search_memory` | 1. Call Gemini 3 to embed `query`<br>2. `SELECT *, vector::similarity::cosine(embedding, $query_emb) AS score FROM content ORDER BY score DESC LIMIT $k` |
| `delete_document` | `forget_memory` | `DELETE content:$id` |

### 2. The "Memory Service" (Agno Agent)
Instead of a raw database wrapper, we will wrap this logic in a **Memory Service** agent.

*   **Role:** The interface between the swarm and the database.
*   **Responsibility:**
    *   Abstracts away the embedding generation (Gemini 3).
    *   Handles "Hybrid Search" (combining full-text search with vector search). SurrealDB supports full-text indexing too (`DEFINE INDEX ... COLUMNS body TYPE FULLTEXT`).
    *   **Self-Correction:** If a search yields no results, the Memory Service can automatically try relaxing the metadata filters or rephrasing the query.

### 3. Implementation Details
*   **Embeddings:** Use `google-generativeai` SDK to fetch embeddings from Gemini.
*   **Database:** Use `surrealdb.js` (or Python equivalent) for interactions.
*   **Filtering:** We need a query builder that translates a JSON filter object (like `{ "type": "report", "year": 2025 }`) into a SurrealQL `WHERE` clause.

### 4. Why this is better for us?
By implementing the **interface** of Chroma but using the **engine** of SurrealDB + Gemini:
*   We keep our stack unified (One DB for Graph + Vectors + Relational).
*   We leverage Gemini's massive context window and high-quality embeddings.
*   We avoid managing a separate vector database infrastructure.
