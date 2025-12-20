# CrewAI Tools: The Agent's Utility Belt

## 1. Synthesis

**Repository:** `crewaiinc/crewai-tools`
**Language:** Python
**Core Purpose:** A standalone library of production-ready tools for AI agents, featuring strong integration with the CrewAI framework but usable independently. It emphasizes "RAG-as-a-Tool" and robust external integrations.

### Key Capabilities
*   **RAG Tools:** A suite of tools (`PDFSearchTool`, `TXTSearchTool`, `GithubSearchTool`, `PGSearchTool`) that handle the entire RAG pipeline (Ingest -> Chunk -> Embed -> VectorStore -> Query) internally. This allows an agent to "chat with a file" or "chat with a repo" without a central knowledge base.
*   **MCP Integration:** Built-in `MCPServerAdapter` allowing CrewAI agents to consume any Model Context Protocol server as a native tool.
*   **Scraping Suite:** Multiple scraping options ranging from simple (`ScrapeWebsiteTool`) to headless browsers (`SeleniumScrapingTool`) to AI-native extractors (`Firecrawl`, `Spider`, `Scrapfly`).
*   **Platform Connectors:** Tools for AWS (Bedrock, S3), Databricks, Snowflake, and Zapier.

### Architectural Highlights
*   **Adapter Pattern:** Uses adapters (`embedchain_adapter`, `lancedb_adapter`) to abstract the underlying vector database mechanics from the tool interface.
*   **Tool Decorators:** Provides a `@tool` decorator for quickly converting Python functions into agent-compatible tools with schema inference.
*   **Standardized Interface:** All tools subclass `BaseTool` (pydantic model), ensuring consistent `name`, `description`, and `_run` methods, which simplifies agent orchestration.

---

## 2. Strategic Ideas for Golden Armada

The "Golden Armada" is building a library of Agno agents. `crewai-tools` offers a masterclass in how to package capabilities for agents.

### A. "Ad-Hoc" RAG vs. "System" RAG
The Armada uses SurrealDB as the "System Memory". However, sometimes an agent just needs to read a specific PDF for one task and then forget it.
*   **Idea:** Implement "Ephemeral RAG Tools".
*   **Mechanism:** When an agent uses `pdf_search(file_path)`, the system spins up an in-memory LanceDB instance (or a temporary SurrealDB namespace), ingests the doc, queries it, and destroys it after the session.
*   **Benefit:** Keeps the main Knowledge Graph clean of transient documents.

### B. The MCP Adapter
CrewAI's `MCPServerAdapter` is the bridge we need for Agno.
*   **Idea:** Port this logic to Agno. Create an `MCPTool` class in Agno that connects to an MCP server (via stdio or SSE), fetches the tool list, and dynamically registers them as Agno tools.
*   **Benefit:** Instantly unlocks the entire MCP ecosystem (Stripe, Slack, Postgres, etc.) for the Golden Armada.

### C. Tiered Scraping Strategy
CrewAI supports 5+ scraping backends. We should adopt this "Fallback" strategy.
*   **Idea:** Create a `UniversalScraper` tool.
*   **Logic:** Try simple `requests` -> If blocked, try `Selenium` -> If blocked, try `Firecrawl/BrightData` (Paid).
*   **Benefit:** Balances cost vs. reliability automatically.

---

## 3. Integration Plan (Agno + SurrealDB + Gemini 3)

We will use `crewai-tools` as a reference implementation for building our own "Armada Toolset".

### Component: `ToolRegistry`

#### 1. The `AgnoMCPAdapter`
We will implement a tool that wraps the `mcp` python SDK.

```python
# Conceptual Implementation
from agno.tools import Tool
from mcp import ClientSession, StdioServerParameters

class MCPToolkit(Tool):
    def __init__(self, server_params: StdioServerParameters):
        self.session = ClientSession(server_params)
        # Dynamic tool registration logic...
```

#### 2. Porting Key Tools to Agno
We will reimplement specific high-value tools from CrewAI into our Agno stack, backed by SurrealDB.

*   **`SurrealSearchTool`:** Instead of `PGSearchTool`, we build a tool that accepts a natural language query, converts it to SurrealQL (via Gemini), executes it, and returns results.
*   **`VisionTool`:** We will use Gemini 3.5's native multimodal capabilities. The tool will simply accept an image path, upload it to Gemini, and return the description, rather than using a separate CLIP/DALL-E pipeline.

#### 3. RAG Standardization
We will enforce that all RAG tools in the Armada use `SurrealDB` vector indexing.
*   **CrewAI approach:** Uses local LanceDB/Chroma by default.
*   **Armada approach:**
    1.  Tool: `IngestFile(path)`.
    2.  Process: Parse -> Chunk -> Embed (Gemini) -> Store in `documents` table in SurrealDB with vector index.
    3.  Tool: `QueryKnowledge(query)`.
    4.  Process: Embed query -> Vector Search `documents` in SurrealDB -> Rerank -> Return.

### Implementation Steps

1.  **Dependency Analysis:** We don't need to install `crewai-tools` directly (heavy dependencies). We will read their source code (e.g., `scrape_website_tool.py`) and reimplement the logic using `httpx` and `BeautifulSoup` within our lightweight `ArmadaTools` package.
2.  **MCP First:** Prioritize building the `MCPToolkit` for Agno. This gives us access to the `brightdata` and `code-executor` servers we analyzed earlier without writing custom integration code for each.
3.  **Refactor `ReconSquad`:** Equip the Recon Squad with the "Tiered Scraper" derived from CrewAI's patterns.
