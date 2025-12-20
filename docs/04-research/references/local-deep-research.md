# Reference Analysis: Local Deep Research

## 1. Synthesis

**Local Deep Research** is a sophisticated, open-source AI-powered research assistant designed to perform deep, iterative analysis on complex topics. Unlike simple "question-answer" bots, this system mimics a human researcher by breaking down a query into sub-questions, conducting multiple rounds of web searching, synthesizing findings, and generating a comprehensive report with citations.

### Core Value Proposition
The primary value of this repository lies in its **"Deep Research"** methodology. It acknowledges that complex questions cannot be answered with a single search query. Instead, it employs a recursive or iterative approach:
1.  **Initial Understanding**: It first attempts to understand the user's broad query.
2.  **Iterative Questioning**: It generates specific, follow-up search questions to fill knowledge gaps.
3.  **Multi-Source Verification**: It aggregates data from various search engines (DuckDuckGo, Google via SerpAPI, Wikipedia, ArXiv) and local documents (RAG).
4.  **Citation & Fact-Checking**: It rigorously tracks sources and attempts to verify claims (though fact-checking is an optional feature).
5.  **Report Generation**: It structures the final output into a coherent document with a table of contents, sections, and references.

### Key Features
*   **Iterative Research Loop**: The system runs for a configurable number of iterations (default 3), generating new questions based on previous findings.
*   **Flexible LLM Backend**: It supports local models via Ollama (privacy-focused) and cloud models (OpenAI, Anthropic).
*   **Search Engine Agnosticism**: It employs a "Strategy Pattern" for search engines, allowing seamless switching between providers or using an "Auto" mode that selects the best engine for the query type (e.g., ArXiv for science, Wikipedia for facts).
*   **Local RAG (Retrieval-Augmented Generation)**: It includes a built-in system for indexing and searching local text/PDF files using FAISS and sentence-transformers.
*   **Real-time UI**: A Flask + Socket.IO web interface provides real-time feedback on the research progress, showing current search queries and findings as they happen.

### Architectural Components
The codebase is structured around several key modules:
*   **`search_system.py`**: The "brain" of the operation. It manages the research loop, maintaining the state of "current knowledge" and deciding what to search for next.
*   **`report_generator.py`**: Responsible for taking the raw findings and synthesizing them into a structured Markdown report. It uses the LLM to determine the optimal table of contents based on the gathered data.
*   **`citation_handler.py`**: A specialized module for processing search results, extracting valid links, and ensuring the LLM cites these sources correctly in its output.
*   **`web_search_engines/`**: A directory containing adapters for different search providers.
*   **`app.py`**: The web server entry point, handling API requests and WebSocket connections for the frontend.
*   **`local_collections.py`**: Configuration for local document sets, effectively acting as a custom search engine.

---

## 2. Strategic & Architectural Ideas for CodeSwarm

The **CodeSwarm** project (migrating to Agno + SurrealDB + Gemini 3) can benefit significantly from the patterns demonstrated in `local-deep-research`.

### 2.1. The "Deep Research" Agent Pattern
The most critical takeaway is the **agentic workflow for research**. In Agno (formerly Phidata), this maps perfectly to a specialized Agent or a Team of Agents.
*   **Concept**: Instead of a single "Search Tool" call, we need a **"Research Orchestrator"**.
*   **Application**: When a CodeSwarm user asks for "Analysis of competitor X" or "Best practices for Y tech stack", a simple LLM response is insufficient. We need an agent that:
    1.  Decomposes the request.
    2.  Spins up sub-tasks (searches).
    3.  Aggregates results.
    4.  Refines its own context.
    5.  Produces a final artifact.

### 2.2. Dynamic Context Compression
`local-deep-research` uses a technique called "Context Compression" or "Knowledge Compression" in `search_system.py`.
*   **Logic**: After every iteration, the system asks the LLM to summarize the "Current Knowledge" into a concise form, discarding irrelevant details but keeping citations.
*   **Benefit**: This prevents the context window from overflowing (though less of an issue with Gemini 1.5's massive context, it reduces cost and noise).
*   **CodeSwarm Fit**: We can implement a `KnowledgeManager` agent in Agno whose sole job is to maintain the "State of Truth" for a running task, updating it as new information comes in from Dev or Research agents.

### 2.3. "Auto" Search Tool Selection
The `search_tool="auto"` logic in `config.py` is brilliant. It uses the LLM (or heuristics) to decide *where* to look.
*   **Logic**: If the query contains "latest news", use Google/DDG. If it's "theorem proof", use ArXiv. If it's "project guidelines", use Local Docs.
*   **CodeSwarm Fit**: Our agents should not just have a generic `search_web` tool. They should have a `smart_search` tool that routes the query to:
    *   **Internet**: For external libraries/docs.
    *   **Codebase (Vector Store)**: For existing code patterns (SurrealDB).
    *   **Project Docs**: For requirements/specs.

### 2.4. Real-time Progress Streaming
The use of Socket.IO in `app.py` allows the user to see "thinking" steps ("Searching for X...", "Reading link Y...").
*   **CodeSwarm Fit**: As we move to Agno, we should leverage Agno's streaming responses or integrate with a similar WebSocket mechanism to keep the user informed during long-running coding tasks.

### 2.5. Section-Based Report Generation
The `IntegratedReportGenerator` in `report_generator.py` doesn't just write a blob of text. It:
1.  Analyzes all findings.
2.  Proposes a Table of Contents (Structure).
3.  Researches *specifically* for each section if needed (though the local-deep-research implementation does a mix of this).
4.  Generates content section-by-section.
*   **CodeSwarm Fit**: For generating documentation (e.g., `docs/03-architecture/new-feature.md`), we should use this "Plan -> Draft -> Refine" structure.

---

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

This section outlines how to rebuild the capabilities of `local-deep-research` using our target stack.

### 3.1. Stack Mapping

| Component | Local Deep Research | CodeSwarm Target | Notes |
| :--- | :--- | :--- | :--- |
| **Framework** | LangChain | **Agno** (Phidata) | Agno provides cleaner agent abstractions. |
| **Database** | SQLite (History) + FAISS (Vectors) | **SurrealDB** | SurrealDB handles both relational data (history) and vector search. |
| **LLM** | Ollama / OpenAI / Anthropic | **Google Gemini 1.5** (Pro/Flash) | Gemini's long context is a game-changer for research. |
| **Search** | Custom Engines | **Agno Tools** | `DuckDuckGo()`, `GoogleSearch()`, etc. |
| **Web/API** | Flask + Socket.IO | **FastAPI** (Agno default) | Agno agents are easily exposed via FastAPI. |

### 3.2. Data Model (SurrealDB)

Instead of `sqlite3`, we will use SurrealDB to store research sessions and vectors.

**Table: `research_sessions`**
```sql
DEFINE TABLE research_sessions SCHEMAFULL;
DEFINE FIELD query ON research_sessions TYPE string;
DEFINE FIELD status ON research_sessions TYPE string; -- 'in_progress', 'completed', 'failed'
DEFINE FIELD mode ON research_sessions TYPE string; -- 'quick', 'deep'
DEFINE FIELD created_at ON research_sessions TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON research_sessions TYPE datetime DEFAULT time::now();
DEFINE FIELD report_content ON research_sessions TYPE string;
DEFINE FIELD metadata ON research_sessions TYPE object;
```

**Table: `research_findings`** (The "Knowledge")
```sql
DEFINE TABLE research_findings SCHEMAFULL;
DEFINE FIELD session_id ON research_findings TYPE record(research_sessions);
DEFINE FIELD iteration ON research_findings TYPE int;
DEFINE FIELD question ON research_findings TYPE string;
DEFINE FIELD content ON research_findings TYPE string;
DEFINE FIELD sources ON research_findings TYPE array;
DEFINE FIELD embedding ON research_findings TYPE array<float>; -- For semantic search over findings
```

**Table: `local_docs`** (RAG)
```sql
DEFINE TABLE local_docs SCHEMAFULL;
DEFINE FIELD title ON local_docs TYPE string;
DEFINE FIELD content ON local_docs TYPE string;
DEFINE FIELD path ON local_docs TYPE string;
DEFINE FIELD embedding ON local_docs TYPE array<float>;
DEFINE INDEX idx_embedding ON local_docs FIELDS embedding MTREE DIMENSION 768 DIST COSINE;
```

### 3.3. Agno Agent Implementation

We will create a `DeepResearchAgent` in Agno.

#### Step 1: Define Tools
We need tools that mimic the `web_search_engines` functionality.

```python
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.google_search import GoogleSearch
# Assuming we have a custom SurrealDB tool wrapper
from codeswarm.tools.surreal_tool import SurrealVectorSearch

def get_search_tools():
    return [
        DuckDuckGoTools(),
        # Add GoogleSearch if API key available
        # SurrealVectorSearch(table="local_docs") # For local RAG
    ]
```

#### Step 2: The Research Orchestrator (The "Deep" Logic)
This is where we port the `search_system.py` logic. Instead of a `while` loop in a script, we can use an Agno Agent with a specific instruction set or a custom `Workflow`.

**Approach A: Recursive Agent**
The agent is instructed to:
1.  Analyze the query.
2.  Generate 3 sub-questions.
3.  Call search tools for each.
4.  Synthesize.
5.  Decide if more info is needed (iterate).

**Approach B: Explicit Workflow (Python Control Flow)**
This is closer to the original `local-deep-research` implementation and often more reliable for "loops".

```python
import time
from typing import List, Dict
from agno.agent import Agent
from agno.models.google import Gemini

class DeepResearcher:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.agent = Agent(
            model=Gemini(id="gemini-1.5-pro-latest"),
            tools=get_search_tools(),
            show_tool_calls=True,
            instructions="""
            You are a Senior Research Analyst.
            Your goal is to answer the user's question exhaustively.
            1. When asked to search, use the available tools.
            2. Verify sources.
            3. Provide citations.
            """
        )
        # Database connection would be initialized here

    def search_iteration(self, current_knowledge: str, focus_questions: List[str]) -> str:
        """Runs one iteration of research."""
        findings = ""
        for q in focus_questions:
            print(f"Searching for: {q}")
            # The agent decides which tool to use for the question
            response = self.agent.run(f"Search for this specific question and summarize findings with URLs: {q}")
            findings += f"\n\nQuestion: {q}\nFindings: {response.content}\n"
        return findings

    def generate_next_questions(self, query: str, current_knowledge: str) -> List[str]:
        """Asks the LLM for the next set of questions."""
        prompt = f"""
        Goal: {query}
        Current Knowledge: {current_knowledge}

        Identify 3 gaps in our knowledge. Return 3 search queries to fill these gaps.
        Return strictly a list of strings.
        """
        response = self.agent.run(prompt)
        # Parse response into list
        # ... implementation detail ...
        return parsed_questions

    def run(self, query: str, max_iterations=3):
        current_knowledge = ""

        # Initial search
        initial_questions = self.generate_next_questions(query, "None")

        for i in range(max_iterations):
            print(f"Iteration {i+1}")
            new_findings = self.search_iteration(current_knowledge, initial_questions)

            # Context Compression / Update
            current_knowledge += new_findings

            # Generate report structure or next questions
            if i < max_iterations - 1:
                initial_questions = self.generate_next_questions(query, current_knowledge)

        # Final Report Generation
        final_report = self.generate_final_report(query, current_knowledge)
        return final_report

    def generate_final_report(self, query: str, knowledge: str) -> str:
        prompt = f"""
        Write a comprehensive report on: {query}
        Based on the following research:
        {knowledge}

        Structure:
        1. Executive Summary
        2. Detailed Findings
        3. References
        """
        return self.agent.run(prompt).content
```

### 3.4. Handling Citations (The "Hard" Part)
`local-deep-research` uses `citation_handler.py` to enforce `[1]`, `[2]` format.
In Agno with Gemini, we can prompt for this, but Gemini also has "Grounding" capabilities.
*   **Recommendation**: Use **Gemini's Grounding with Google Search** if possible (vertexai/studio). It automatically provides citations.
*   **Fallback**: If using generic tools, prompt the agent: "You MUST cite sources. When you use information from a URL, append `[Source: URL]`."

### 3.5. Local Document Search (RAG) with SurrealDB
To replicate the `local_collections.py` feature:

1.  **Ingestion Script**: A script that scans `docs/` or `codeswarm/`, chunks text, generates embeddings (using `google-generativeai` embeddings API or a local model like `all-MiniLM-L6-v2`), and inserts into SurrealDB `local_docs` table.
2.  **Agno Tool**: Create a `SearchLocalDocs` tool.

```python
from agno.tools import Toolkit

class LocalDocsToolkit(Toolkit):
    def __init__(self, db_client):
        super().__init__(name="local_docs")
        self.db = db_client

    def register(self, agent):
        agent.register_tool(self.search_docs)

    def search_docs(self, query: str) -> str:
        """Searches local documentation for the query."""
        # 1. Generate embedding for query
        # 2. Perform vector search in SurrealDB
        # query = "SELECT *, vector::similarity::cosine(embedding, $query_vec) AS score FROM local_docs ORDER BY score DESC LIMIT 5"
        # 3. Return concatenated content
        return "Content found in docs..."
```

---

## 4. Specific Implementation Steps

To integrate these ideas into CodeSwarm, follow this roadmap:

### Phase 1: Foundation
1.  **Setup SurrealDB**: Ensure SurrealDB is running and accessible. Define the schemas for `research_sessions` and `local_docs`.
2.  **Agno Setup**: Verify Agno is installed and configured with Gemini API keys.

### Phase 2: The Researcher Agent
3.  **Create `codeswarm/agno-agents/104_deep_researcher_agent.py`**:
    *   This should be a subclass of `SwarmAgent` (if using the repo's pattern) or a standalone Agno Agent.
    *   Implement the iterative loop (Plan -> Search -> Analyze -> Repeat).
    *   Integrate `DuckDuckGoTools`.

### Phase 3: RAG Integration
4.  **Create Ingestion Tool**: Build `scripts/ingest_docs_to_surreal.py`.
    *   Walk `docs/`.
    *   Chunk text.
    *   Embed using Gemini Embeddings.
    *   Store in SurrealDB.
5.  **Create RAG Tool**: Build `codeswarm/tools/surreal_rag.py`.
    *   Implement vector search.
    *   Attach to the `DeepResearcherAgent`.

### Phase 4: Reporting
6.  **Implement Report Generator**: Add a final step to the agent to synthesize a Markdown report.
7.  **Output**: Save reports to `docs/05-reports/research/`.

### Phase 5: UI (Optional/Later)
8.  **API Endpoint**: Expose the agent via a FastAPI route in `codeswarm/server.py`.
9.  **Streaming**: Implement Server-Sent Events (SSE) to stream the research progress to a frontend.

## 5. Detailed Logic Breakdown (from Source)

### 5.1. `search_system.py` - The Loop
The `AdvancedSearchSystem` class is the core.
*   **`analyze_topic(query)`**: Entry point.
    *   Initializes `findings = []` and `current_knowledge = ""`.
    *   Loops `SEARCH_ITERATIONS` times.
    *   **`_get_follow_up_questions`**:
        *   Prompt: "Critically reflect current knowledge... what X high-quality questions remain unanswered?"
        *   Uses LLM to generate questions.
    *   **Loop over Questions**:
        *   `search.run(question)`: Gets results (links/snippets).
        *   `citation_handler.analyze_followup`:
            *   Takes `search_results` and `previous_knowledge`.
            *   Uses LLM to answer the specific question using sources.
            *   Returns content + citations.
        *   Appends to `findings`.
    *   **`_compress_knowledge`**:
        *   Prompt: "Provide a high-quality long explanation based on sources... keep citations."
        *   Updates `current_knowledge`.
    *   **`_save_findings`**: Dumps intermediate state to disk.

### 5.2. `citation_handler.py` - The Verifier
*   **`_create_documents`**: Converts search results (dicts) into LangChain `Document` objects.
*   **`_format_sources`**: Creates a string like `[1] Source Title - Content...`.
*   **`analyze_followup`**:
    *   Prompt includes: `Previous Knowledge`, `New Sources`, `Question`.
    *   Instruction: "Include citations using numbers in square brackets [1]... Never make up sources."

### 5.3. `report_generator.py` - The Architect
*   **`generate_report`**:
    *   **Step 1: Determine Structure**.
        *   Feeds summary of findings to LLM.
        *   Asks for a "Structure" (TOC) with Sections and Subsections + Purpose.
    *   **Step 2: Research Sections**.
        *   Iterates through the generated TOC.
        *   For each section, generates *new* specific research questions.
        *   Runs `search_system` (with fewer iterations) for that section.
    *   **Step 3: Generate Content**.
        *   Synthesizes text for each section using general + specific research.
    *   **Step 4: Format**.
        *   Assembles the Markdown.

## 6. Conclusion

`local-deep-research` provides a robust blueprint for an autonomous research agent. By adapting its iterative loop, context management, and structured reporting logic to the **Agno + SurrealDB + Gemini** stack, CodeSwarm can gain a powerful capability: the ability to autonomously generate deep, cited, and well-structured technical documentation and research reports. This moves the system from "executing code" to "understanding problems".
