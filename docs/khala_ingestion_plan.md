# Khala Ingestion Plan

## Objective
To ingest the "wisdom" and knowledge accumulated from the analysis of 300+ arXiv articles into the Khala memory system, enabling agents to retrieve and apply state-of-the-art research during their operation.

## Strategy
1.  **Vectorization:** Convert paper abstracts, "Key Offerings", and "Relevance" sections into vector embeddings using the `embedding` model configured in Khala.
2.  **Storage:** Store these records in SurrealDB.
    *   **Tier:** `MemoryTier.LONG_TERM`.
    *   **Category:** `research`.
    *   **Tags:** `[paper_id, topic, arxiv]`.
3.  **Retrieval:** `KnowledgeAgent` will query this knowledge using semantic search when facing high-level design decisions or architectural problems.

## Execution Steps
1.  **Parse Reports:**
    *   Iterate through all `.md` files in `docs/articles/`.
    *   Extract:
        *   `Title`
        *   `Abstract`
        *   `Relevance to CodeSwarm`
        *   `Key Offerings`
2.  **Prepare Memory Objects:**
    *   Construct a memory content string: `Title: {title}\nAbstract: {abstract}\nRelevance: {relevance}\nOfferings: {offerings}`.
    *   Assign importance score based on "Relevance" (High relevance = 0.9, Low = 0.3).
3.  **Ingest via Integration:**
    *   Create a script `scripts/ingest_research.py` that imports `codeswarm.khala_integration`.
    *   Use `KhalaSystem.get_instance().memory_provider.add_memory(...)` (or direct SurrealDB client usage if needed).
4.  **Verification:**
    *   Run a query via `KnowledgeAgent` asking "What are the risks of agent sabotage?" and verify it retrieves `2511.09904`.

## Timeline
*   **Immediate:** Ingest the initial batch (20 papers).
*   **Continuous:** As `harvest_arxiv.py` processes more papers, run ingestion periodically.
