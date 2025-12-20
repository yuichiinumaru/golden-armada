# Bright Data MCP: Real-Time Web Intelligence

## 1. Synthesis

**Repository:** `brightdata-com/brightdata-mcp`
**Language:** JavaScript (Node.js)
**Core Purpose:** An MCP server providing robust, real-time web scraping and browser automation capabilities, specifically designed to bypass anti-bot measures and geo-restrictions.

### Key Capabilities
*   **Web Unlocker:** Tools (`scrape_as_markdown`, `scrape_as_html`) that transparently handle proxies, CAPTCHAs, and fingerprinting to fetch content from hard-to-scrape sites.
*   **Scraping Browser:** A persistent remote browser session controlled via MCP tools (`navigate`, `click`, `type`, `screenshot`, `get_html`). This allows agents to interact with dynamic SPAs (Single Page Applications).
*   **Structured Data APIs:** A massive suite of pre-built "Datasets" accessible as tools (e.g., `web_data_linkedin_profile`, `web_data_amazon_product`, `web_data_youtube_comments`). These return structured JSON instead of raw HTML.
*   **Search Engine Scraping:** dedicated tool for extracting SERP data (Google, Bing, Yandex).

### Architectural Highlights
*   **Session Management:** The `Browser_session` class maintains state (cookies, storage) across tool calls, enabling multi-step workflows (login -> navigate -> scrape).
*   **Domain-Aware:** Intelligent session handling that groups browser contexts by domain to avoid cross-contamination or detection.
*   **Polling Pattern:** The `web_data_*` tools use an async trigger-and-poll mechanism to handle long-running scraping jobs while keeping the MCP interface responsive.

---

## 2. Strategic Ideas for Golden Armada

The Golden Armada's "Scout Squad" needs eyes on the web. Standard scraping (Requests/BeautifulSoup) fails on modern defensive sites. Bright Data offers a "Mercenary Scout" capability.

### A. The "Unblockable" Scout
Agno agents often fail when a URL returns "403 Forbidden" (Cloudflare/Akamai).
*   **Idea:** Implement a "Fallback Scout". If the lightweight internal scraper fails, the agent automatically switches to `scrape_as_markdown` via Bright Data.
*   **Benefit:** Increases mission success rate from ~60% to ~99% for external research tasks.

### B. Structured "Dark Matter" Ingest
Social media and e-commerce data are usually "dark" to standard crawlers.
*   **Idea:** Use the specialized `web_data_*` tools to populate the Knowledge Graph (SurrealDB) with rich entities.
*   **Example:** `web_data_linkedin_company_profile` -> Graph Node `Company` with fields `employees`, `revenue`, `locations`. This is far cleaner than parsing HTML manually.

### C. Visual Verification Agent
The `scraping_browser_screenshot` tool allows for visual ground truth.
*   **Idea:** When an agent scrapes a controversial or critical piece of data (e.g., a stock price or news headline), it takes a screenshot and stores it in SurrealDB as an artifact.
*   **Benefit:** Provides an audit trail. "Why did the agent think the price was $50?" -> "Here is the screenshot from 10:00 AM."

---

## 3. Integration Plan (Agno + SurrealDB + Gemini 3)

We will integrate Bright Data as a premium toolset for specific squads.

### Component: `ReconSquad`

#### 1. Integration with Agno
We will register the Bright Data MCP server as a remote toolset.

```python
# Conceptual Agno Integration
from agno.agent import Agent
from agno.tools.mcp import MCPTool

recon_agent = Agent(
    role="Reconnaissance Scout",
    tools=[MCPTool(server_url="...", tools=["search_engine", "scrape_as_markdown", "web_data_linkedin_company_profile"])],
    instructions="Find the CEO of Acme Corp and get their latest news."
)
```

#### 2. The `WebSource` Table (SurrealDB)
We need to track where data comes from and how much it cost (Bright Data is paid).

```sql
DEFINE TABLE web_source SCHEMAFULL;
DEFINE FIELD url ON TABLE web_source TYPE string;
DEFINE FIELD method ON TABLE web_source TYPE string; -- 'standard' or 'brightdata'
DEFINE FIELD cost_credits ON TABLE web_source TYPE number;
DEFINE FIELD snapshot ON TABLE web_source TYPE string; -- Link to screenshot artifact
DEFINE FIELD parsed_content ON TABLE web_source TYPE string;
```

#### 3. The "Deep Browse" Flow
For complex research tasks that require navigation (e.g., "Log into this portal and download the PDF").

1.  **Agent:** Calls `scraping_browser_navigate(url)`.
2.  **MCP:** Connects to remote CDP endpoint.
3.  **Agent:** Calls `scraping_browser_screenshot()` to "see" the page.
4.  **Gemini:** Analyzes the screenshot -> "I need to click the blue button".
5.  **Agent:** Calls `scraping_browser_click(selector=".blue-btn")`.
6.  **Loop:** Repeats until target data is found.

### Implementation Steps

1.  **Environment Setup:** Add `BRIGHT_DATA_API_KEY` to the Armada's secure vault.
2.  **Tool Wrapping:** Create a `WebScraper` class in the Agno codebase that abstracts the choice between "Cheap/Fast" (internal) and "Heavy/Sure" (Bright Data).
3.  **Cost Guardrails:** Implement a budget manager in the `ReconSquad`. "If we have spent > $5 today, ask for user permission before using Bright Data."

### Refined Workflow: "Entity Enrichment"
1.  **User:** "Analyze competitor X."
2.  **Orchestrator:** Checks SurrealDB. "Competitor X exists but data is stale."
3.  **ReconAgent:**
    *   Calls `search_engine(query="Competitor X LinkedIn")`.
    *   Extracts URL.
    *   Calls `web_data_linkedin_company_profile(url)`.
    *   Calls `web_data_glassdoor_reviews(url)` (via generic scraper or custom dataset).
4.  **Integration:** JSON results are mapped to the `Organization` graph schema and merged into SurrealDB.
