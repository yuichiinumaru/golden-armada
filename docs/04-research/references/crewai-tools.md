# Reference Analysis: CrewAI Tools

## 1. Synthesis

**CrewAI Tools** is the comprehensive tooling library for the CrewAI agent framework. It provides a massive collection of "ready-to-use" tools that agents can employ to interact with the external world (web, databases, APIs, files).

### Core Value Proposition
This library solves the **"Agency"** problem. An AI model is just a text processor until it has tools. CrewAI Tools provides a standardized, battle-tested suite of integrations so developers don't have to write their own wrappers for common services like Google Search, GitHub, PostgreSQL, or local file management.

### Key Features
*   **Extensive Tool Catalog**: Over 30+ built-in tools ranging from `FileReadTool` to `VisionTool`, covering:
    *   **File System**: Read/Write files, list directories.
    *   **Search**: Google (Serper), DuckDuckGo, Tavily, Exa.
    *   **Scraping**: ScrapeWebsite, Selenium, Firecrawl, Spider.
    *   **Database**: PostgreSQL, MySQL (RAG-based search over DBs).
    *   **RAG**: Native support for "Chat with Docs" via Embedchain (PDF, CSV, TXT, MDX, Notion, etc.).
    *   **Connectors**: GitHub, Zapier, Slack.
*   **Adapter Pattern**: Uses adapters (`EmbedchainAdapter`, `LancedbAdapter`) to decouple the tool interface from the underlying implementation logic.
*   **MCP Support**: Recently added support for the Model Context Protocol (MCP), allowing it to consume tools from other MCP servers.
*   **Base Class Design**: All tools inherit from a common `BaseTool` (Pydantic-based), ensuring consistent schema generation for LLM function calling.

### Architectural Components
The structure is modular, with each tool in its own subdirectory under `crewai_tools/tools/`.
*   **`crewai_tools/tools/`**: The implementation of specific tools.
*   **`crewai_tools/adapters/`**: Bridges to 3rd party libraries (like Embedchain for RAG).
*   **`BaseTool`**: The parent class that handles argument validation and schema generation.
*   **`MCPServerAdapter`**: A bridge to connect to MCP servers.

---

## 2. Strategic & Architectural Ideas for CodeSwarm

**CodeSwarm** (Agno + SurrealDB + Gemini 3) currently has a "build it yourself" philosophy. While good for control, it slows down feature expansion. Analyzing `crewai-tools` reveals several patterns we should adopt.

### 2.1. The "Tool Library" Pattern
Instead of writing tools inside each agent file, we should have a centralized `codeswarm/tools/` directory (which we partly have, but it needs expansion).
*   **Idea**: Create a standard interface for CodeSwarm tools that is compatible with Agno.
*   **Application**: Port the best tools from CrewAI (File, Directory, Code Interpreter) to CodeSwarm. This immediately boosts our agents' capabilities.

### 2.2. RAG-as-a-Tool
CrewAI's `PDFSearchTool` doesn't just "read text". It chunks, embeds, stores in a vector DB (Chroma/LanceDB), and performs semantic search.
*   **Idea**: CodeSwarm should have "Smart Read" tools.
*   **Application**: When a `DevAgent` reads a 5,000-line file, it shouldn't dump the whole thing into the context. It should index it into SurrealDB (ephemeral table) and query relevant chunks. This uses Gemini's context window more efficiently.

### 2.3. Database Introspection Tools
The `PGSearchTool` allows natural language queries over SQL databases.
*   **CodeSwarm Fit**: Since we use SurrealDB, we should build a `SurrealSearchTool`.
*   **Usage**: "Find all tasks related to 'frontend' that failed last week." The agent shouldn't write raw SQL; it should use a semantic search tool that maps the question to the DB schema.

### 2.4. Code Interpreter (The Holy Grail)
CrewAI has a `CodeInterpreterTool` (often Docker-based).
*   **Strategic Priority**: As identified in the `mcp_code_executor` report, this is critical.
*   **Integration**: We can either adapt the CrewAI implementation or build our own using the architecture defined in the previous report.

---

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

We will build a "Standard Library" of tools for CodeSwarm agents.

### 3.1. Stack Mapping

| Component | CrewAI Tools | CodeSwarm Target | Notes |
| :--- | :--- | :--- | :--- |
| **Base Class** | `pydantic.BaseModel` | **Agno `Toolkit` / `Function`** | Agno uses Pydantic natively. |
| **Vector DB** | Chroma / LanceDB | **SurrealDB** | SurrealDB handles vector search natively. |
| **Embeddings** | OpenAI / Cohere | **Gemini Embeddings** | Stay within the Google ecosystem. |
| **Scraping** | Selenium / Firecrawl | **Playwright** | As planned in `brightdata-mcp` report. |

### 3.2. Data Model (SurrealDB)

We need to store tool configurations (API keys, preferences) and potentially cached results.

**Table: `tool_configs`**
```sql
DEFINE TABLE tool_configs SCHEMAFULL;
DEFINE FIELD tool_name ON tool_configs TYPE string;
DEFINE FIELD config ON tool_configs TYPE object; -- JSON blob for flexibility
DEFINE FIELD created_at ON tool_configs TYPE datetime DEFAULT time::now();
```

### 3.3. Agno Agent Implementation

We will implement a `ToolManager` that agents can use to request tools dynamically.

#### Step 1: File Tools (The Basics)
Port `FileReadTool` and `DirectorySearchTool`.

```python
from agno.tools import Toolkit
import os
import glob

class FileSystemToolkit(Toolkit):
    def __init__(self, root_dir: str = "."):
        super().__init__(name="filesystem")
        self.root = root_dir

    def list_files(self, recursive: bool = False):
        """Lists files in the workspace."""
        # ... logic ...
        return ["src/main.py", "README.md"]

    def read_file(self, file_path: str):
        """Reads a file securely."""
        # ... logic ...
        return "content..."
```

#### Step 2: The "Ask Docs" Tool (RAG)
This mimics `PDFSearchTool` but uses SurrealDB.

```python
from agno.tools import Toolkit
# hypothetical import
from codeswarm.services.surreal import VectorStore

class DocumentationToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="docs_search")
        self.vector_store = VectorStore(table="doc_vectors")

    def search_docs(self, query: str):
        """Semantically searches the project documentation."""
        results = self.vector_store.search(query, limit=3)
        return "\n\n".join([r['content'] for r in results])
```

---

## 4. Specific Implementation Steps

### Phase 1: Core File & Shell Tools
1.  **Create**: `codeswarm/tools/filesystem.py` (Safe file operations).
2.  **Create**: `codeswarm/tools/shell.py` (Safe command execution, maybe reusing the Docker logic from `mcp_code_executor`).

### Phase 2: Knowledge Tools (RAG)
3.  **Schema**: Ensure SurrealDB tables for `doc_vectors` exist.
4.  **Create**: `codeswarm/tools/rag.py`.
    *   Function: `ingest_file(path)` (Chunks + Embeds -> DB).
    *   Function: `query_knowledge(query)` (Embeds -> DB Search).

### Phase 3: The "Toolbox" Agent
5.  **Update `AdminAgent`**: Give it the ability to *assign* tools to DevAgents.
    *   *Idea*: The AdminAgent constructs the DevAgent at runtime, passing `tools=[FileSystemToolkit(), RagToolkit()]`.

### Phase 4: Import CrewAI Tools (Optional)
6.  Since CrewAI tools are Pydantic-based, we can likely write a **Wrapper** to use them directly in Agno if we really need a specific integration (e.g., `SerperDevTool`) without rewriting it.
    *   *Action*: Investigate writing a `CrewAIToolAdapter` for Agno.

## 5. Detailed Logic Breakdown (from Source)

### 5.1. `base_tool.py` (Assumed pattern based on file list)
*   **Validation**: Uses Pydantic to validate inputs before the tool logic runs. This prevents the LLM from passing invalid types.
*   **CodeSwarm Note**: Agno does this too. We must define Pydantic models for all our tool inputs.

### 5.2. `adapters/embedchain_adapter.py`
*   **Abstraction**: Wraps the `embedchain` library.
*   **Query**: `query(question: str) -> str`.
*   **Add**: `add(data_type: str, data_source: str)`.
*   **CodeSwarm Lesson**: Don't expose the vector DB complexity to the agent. Expose simple `add()` and `query()` functions.

## 6. Conclusion

`crewai-tools` is a goldmine of implementation details for AI tools. We shouldn't blindly copy it, but rather **port the most essential capabilities** (Filesystem, RAG, Web Search) into our Agno + SurrealDB stack. The most valuable insight is the **"RAG as a Tool"** pattern, where the agent doesn't just read a file, but interacts with a semantic index of that file. This enables handling much larger codebases than simple context stuffing.
