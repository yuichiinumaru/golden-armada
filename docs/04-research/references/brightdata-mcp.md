# Reference Analysis: Bright Data MCP

## 1. Synthesis

**Bright Data MCP** is an official Model Context Protocol (MCP) server provided by Bright Data, a leading web data platform. It exposes a suite of tools for **web scraping, browser automation, and data extraction** to LLM-based agents.

### Core Value Proposition
The primary value is **"Web Access for AI"**. LLMs have a knowledge cutoff and cannot natively browse the live web effectively due to anti-bot measures (CAPTCHAs, IP bans). Bright Data solves this by providing an API that handles the infrastructure of scraping (proxy rotation, unblocking, browser fingerprinting) and exposing it as simple function calls (`scrape_as_markdown`, `search_engine`).

### Key Features
*   **Web Unlocker**: Automatically bypasses CAPTCHAs and bot detection systems.
*   **Browser Automation**: Provides remote browser control (Playwright-compatible) via CDP (Chrome DevTools Protocol). Tools include `navigate`, `click`, `type`, `screenshot`, etc.
*   **SERP Access**: Dedicated tool for search engine results (Google, Bing, Yandex) returned in Markdown.
*   **Structured Data Datasets**: A massive library of pre-built "Dataset" tools (`web_data_amazon_product`, `web_data_linkedin_profile`, etc.) that return structured JSON for specific domains, avoiding the need for the LLM to parse HTML.
*   **MCP Standard**: Built on the `FastMCP` framework, making it compatible with any MCP client (Claude Desktop, etc.).

### Architectural Components
The codebase is a Node.js application (`server.js`).
*   **`server.js`**: The main entry point using `FastMCP`. It registers tools and handles the API token authentication.
*   **`browser_session.js`**: Manages remote browser sessions via `playwright.chromium.connectOverCDP`. It handles connection resilience and domain-based session isolation.
*   **`browser_tools.js`**: Wraps Playwright actions (click, type, navigate) into MCP tools.
*   **Dataset Tools Generator**: A loop in `server.js` iterates over a list of dataset definitions and dynamically creates `web_data_*` tools. This is a smart way to expose hundreds of specific scraping capabilities without writing boilerplate for each.

---

## 2. Strategic & Architectural Ideas for CodeSwarm

**CodeSwarm** (Agno + SurrealDB + Gemini 3) aims to be a comprehensive development system. Access to live web data is crucial for "Research" and "Documentation" agents.

### 2.1. The "Web Access" Pattern
Currently, CodeSwarm agents might rely on the LLM's internal knowledge or simple search tools.
*   **Idea**: Integrate a robust web scraping capability.
*   **Application**: A `ResearcherAgent` needs to read the *latest* documentation for a library released last week. Standard `requests.get` will fail on Cloudflare-protected sites. A service like Bright Data (or a self-hosted alternative like `browserless`) is needed.
*   **CodeSwarm Fit**: We should define a `WebScraperTool` in Agno that abstracts the provider.

### 2.2. Dynamic Tool Generation (The "Dataset" Pattern)
The way Bright Data generates `web_data_*` tools dynamically is excellent.
*   **Idea**: CodeSwarm should have a `ToolRegistry` that can dynamically generate tools based on configuration (stored in SurrealDB).
*   **Application**: Instead of writing a Python class for every single action, we can define "API Action Tools" in the DB (e.g., "GitHub Issue Search", "PyPI Package Info") and have an `AgentFactory` load them at runtime.

### 2.3. Browser Session Management
The `Browser_session` class handles the complexity of keeping a browser open across multiple tool calls.
*   **Idea**: Agents need "Stateful Tooling".
*   **Application**: If an agent is navigating a documentation site, it shouldn't restart the browser for every page. Agno supports stateful agents; we need to ensure our tools leverage this (e.g., passing a `session_id` or holding a handle to a Playwright page).

### 2.4. Structured Data over Raw HTML
Bright Data emphasizes getting *structured* data (markdown or JSON) rather than raw HTML.
*   **Strategic Requirement**: Never feed raw HTML to an LLM if possible (token waste).
*   **CodeSwarm Standard**: All scraping tools must return either Markdown (for reading) or JSON (for data). We should use libraries like `trafilatura` or `beautifulsoup4` (or `jina.ai/reader` API) to convert HTML to LLM-friendly text.

---

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

We will enhance CodeSwarm's ability to interact with the outside world.

### 3.1. Stack Mapping

| Component | Bright Data MCP | CodeSwarm Target | Notes |
| :--- | :--- | :--- | :--- |
| **Provider** | Bright Data (Cloud) | **Firecrawl** / **Jina Reader** / **Playwright** | For a self-contained repo, we might prefer Playwright or a free scraping API (Jina) to avoid forcing paid sub on users. |
| **Interface** | MCP | **Agno Toolkit** | `WebTools` class. |
| **Browser** | Remote CDP | **Local/Docker Headless Chrome** | Run locally for cost/privacy. |
| **Logic** | Node.js | **Python** | |

### 3.2. Data Model (SurrealDB)

Track what the agents have read from the web to avoid re-scraping.

**Table: `web_cache`**
```sql
DEFINE TABLE web_cache SCHEMAFULL;
DEFINE FIELD url ON web_cache TYPE string;
DEFINE FIELD content_hash ON web_cache TYPE string;
DEFINE FIELD markdown_content ON web_cache TYPE string;
DEFINE FIELD metadata ON web_cache TYPE object;
DEFINE FIELD fetched_at ON web_cache TYPE datetime DEFAULT time::now();
DEFINE INDEX idx_url ON web_cache COLUMNS url UNIQUE;
```

### 3.3. Agno Agent Implementation

We will create a `WebSurferToolkit`.

#### Step 1: The Scraper Tool
Using `crawl4ai` (a Python library popular with Agno) or simple `playwright`.

```python
from agno.tools import Toolkit
from agno.utils.log import logger
# hypothetical import, or we implement a wrapper around playwright
from crawl4ai import AsyncWebCrawler

class WebSurferToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="web_surfer")

    async def browse(self, url: str):
        """Reads a webpage and returns markdown."""
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return result.markdown

    async def search_google(self, query: str):
        """Searches Google and returns top 5 results with snippets."""
        # Use DuckDuckGo (free) or SerpAPI
        pass
```

#### Step 2: The Researcher Agent
```python
from agno.agent import Agent
from codeswarm.tools.web_surfer import WebSurferToolkit

researcher = Agent(
    role="Tech Researcher",
    tools=[WebSurferToolkit()],
    instructions="""
    1. Search for the topic.
    2. Visit relevant documentation pages.
    3. Synthesize the findings.
    """
)
```

---

## 4. Specific Implementation Steps

### Phase 1: Basic Web Tools
1.  **Dependency**: Add `duckduckgo-search` and `beautifulsoup4` to `requirements.txt`.
2.  **Tool**: Create `codeswarm/tools/web_search.py`.
    *   Implement `search_web(query)`.
    *   Implement `read_url(url)` (using `requests` + `bs4` -> markdown).

### Phase 2: Headless Browser (Advanced)
3.  **Dependency**: Add `playwright`.
4.  **Tool**: Update `read_url` to use Playwright if the page is dynamic (detects JS requirement).
5.  **Schema**: Create `web_cache` table in SurrealDB to cache results (reduce latency).

### Phase 3: The "Deep Research" Integration
6.  Connect this Web Toolkit to the `DeepResearchAgent` planned in the previous report (`local-deep-research`). The `DeepResearcher` needs these exact tools to function.

## 5. Detailed Logic Breakdown (from Source)

### 5.1. `browser_session.js` - Resilience
*   **Reconnection**: The code handles `Browser connection lost... reconnecting...`.
*   **Domain Isolation**: `_getDomainSession` creates separate browser contexts for different domains.
    *   *Lesson*: In CodeSwarm, if we use Playwright, we should use a single `Browser` instance but create new `Contexts` for different tasks or agents to ensure cookies/state don't leak between tasks.

### 5.2. `server.js` - Tool Definitions
*   **Schema**: Uses `zod` for input validation. In Agno, we use Pydantic models or type hints.
*   **Execution**: Simple wrapper around `axios` calls to Bright Data API.

## 6. Conclusion

Bright Data MCP demonstrates how to expose a **Data-as-a-Service** platform to AI agents. For CodeSwarm, we will emulate this by building a **Local Web Scraper Toolkit**. While we won't use Bright Data's paid API by default (to keep CodeSwarm open/free), we will adopt the **interface** (Markdown output, search + browse separation) and the **architecture** (resilient browser sessions) using open-source tools like Playwright and Crawl4AI.
