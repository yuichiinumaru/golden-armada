# Local Deep Research: Recursive Information Retrieval

## Synthesis
The `local-deep-research` repository is a Python-based implementation of a recursive research agent, inspired by OpenAI's Deep Research. It is designed to run locally (using Ollama) or with cloud LLMs (OpenAI, Anthropic).

**Key Components:**
*   **Search Engine Abstraction:** A unified interface (`search_system.py`) that delegates to various backends: Wikipedia, Arxiv, DuckDuckGo, Google (SerpAPI), and **Local RAG** (vector search over local documents).
*   **Recursive Logic:** The core `AdvancedSearchSystem` implements a loop:
    1.  Analyze query and current knowledge.
    2.  Generate "follow-up questions" (sub-queries).
    3.  Execute searches.
    4.  Synthesize findings and update "Accumulated Knowledge".
    5.  Repeat for $N$ iterations or until satisfied.
*   **Report Generation:** A dedicated `IntegratedReportGenerator` that structures the final output into sections, performs focused searches for each section, and compiles a comprehensive markdown report with citations.
*   **Citation Handling:** A `CitationHandler` manages the source links, ensuring every claim is backed by a URL or document reference.

## Strategic Ideas for Golden Armada
This "Breadth + Depth" search pattern is exactly what our `ResearchSquad` needs. Instead of a single-shot "web search tool", we need a **Research Process**.

1.  **The "Researcher" Agent Logic:** We should port the `analyze_topic` loop into an Agno agent.
    *   *State:* `current_knowledge` (text blob), `questions_asked` (list), `iteration` (int).
    *   *Action:* At each step, the agent decides whether to "compress knowledge" or "ask new questions".
2.  **Local Knowledge Injection:** The repository supports `local_collections.py` to index local PDFs/docs. We can map this to our **SurrealDB Vector Store**.
    *   *Ingestor Squad* reads PDFs -> Chunks -> Embeds -> SurrealDB.
    *   *Research Squad* queries SurrealDB as just another "Search Engine" alongside Google.
3.  **Citation-First Architecture:** The system refuses to "make up" sources. It uses a `CitationHandler` to link specific sentences to source IDs. We should enforce this in our `Writer` agents to prevent hallucinations.
4.  **Multi-Modal Inputs:** The system can ingest PDFs and web pages. We should ensure our `Ingestor` agent handles `playwright` (for dynamic web pages) and `pypdf` (for documents) transparently.

## Integration Plan (Agno + SurrealDB + Gemini 3)

### 1. The `ResearchFlow` (SurrealDB + Python)
We will implement the recursive loop as a Python generator or Agno Workflow.

```python
class DeepResearchAgent(Agent):
    def research(self, topic: str, depth: int = 3):
        knowledge = ""
        for i in range(depth):
            # 1. Generate Questions
            questions = self.run(f"Given what we know: {knowledge}, what should we ask next about {topic}?")

            # 2. Parallel Search (Google + SurrealDB)
            results = self.tools.search_all(questions)

            # 3. Synthesize & Cite
            new_knowledge = self.run(f"Synthesize these results into the knowledge base: {results}")
            knowledge += new_knowledge

        return self.write_report(knowledge)
```

### 2. The `CitationManager` Tool
We will create a specific tool that formats search results into indexed `Document` objects and forces the LLM to reference them by `[ID]`.

### 3. Unified Search Interface
We will expose a single `search_tool` to the agents that routes queries:
*   If query looks like "project specs" -> Search SurrealDB (Vector).
*   If query looks like "latest react version" -> Search Google (SerpAPI).

### 4. Why this fits Golden Armada?
*   **Gemini 3 Context:** The "Accumulated Knowledge" grows large. Gemini's 1M+ token window is perfect for holding the entire research history without aggressive compression (which `local-deep-research` has to do for smaller local models).
*   **SurrealDB Persistence:** We can store the *intermediate* research steps in SurrealDB, allowing a user to "resume" a research session or fork it in a different direction.
