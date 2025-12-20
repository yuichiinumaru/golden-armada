# FastAPI-MCP: Zero-Config MCP Server Generation

## 1. Synthesis

**Repository:** `tadata-org/fastapi_mcp`
**Language:** Python
**Core Purpose:** A library that automatically exposes existing FastAPI applications as MCP servers. It inspects FastAPI routes, schemas, and docstrings to generate MCP Tools without requiring manual tool definition.

### Key Capabilities
*   **Auto-Conversion:** Transforms `@app.get` and `@app.post` endpoints into MCP Tools (`list_products`, `create_order`).
*   **Schema Preservation:** Translates Pydantic models used in FastAPI into JSON Schema for MCP tools, preserving descriptions, types, and constraints.
*   **Authentication:** Supports passing headers and auth tokens from the MCP client to the underlying FastAPI app.
*   **FastAPI Native:** Uses the `FastApiMCP` class which wraps a standard `FastAPI` app. It hooks into the ASGI lifecycle.
*   **Transport:** Supports SSE (Server-Sent Events) natively for connecting to clients like Cursor or Claude Desktop.

### Architectural Highlights
*   **`FastApiMCP` Wrapper:** Acts as a bridge. It reads the `app.openapi()` schema and converts paths/verbs into MCP Tool definitions.
*   **ASGI Integration:** Instead of making HTTP requests to `localhost`, it calls the FastAPI app directly via ASGI (in-memory), which is faster and cleaner.
*   **Filtering:** Allows including/excluding specific routes via `include_tags`, `exclude_operations`.

---

## 2. Strategic Ideas for Golden Armada

The Golden Armada is built on Agno, but exposing *our* agents and tools to the outside world (e.g., to be used by Cursor or another agent system) is a powerful capability.

### A. "Armada as a Service"
We can use `fastapi-mcp` to expose the Golden Armada's capabilities as an MCP server.
*   **Idea:** Run a `fastapi-mcp` wrapper around our main Orchestrator API.
*   **Benefit:** A developer using Cursor IDE can type `@Armada create a research plan for X` directly in their editor, and the Armada executes it.

### B. Internal Microservice Bridge
If we have existing Python microservices (e.g., a legacy data processing API), we don't need to rewrite them as Agno tools.
*   **Idea:** Wrap the legacy FastAPI app with `fastapi-mcp`.
*   **Mechanism:** The Agno agents use the `MCPToolkit` (client) to talk to the legacy app (server). This standardizes all internal communication on MCP.

### C. Self-Documenting Tools
The library proves that Pydantic models + Docstrings = Tool Definitions.
*   **Idea:** Enforce strict Pydantic models for *all* Agno tools in the Armada.
*   **Benefit:** We can auto-generate documentation and even a "Tool Catalog" website for the Armada users.

---

## 3. Integration Plan (Agno + SurrealDB + Gemini 3)

We will use this library to **expose** the Armada, not just consume tools.

### Component: `ArmadaGateway`

#### 1. The MCP Endpoint
We will add an MCP endpoint to the Golden Armada's main API.

```python
# main.py
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from armada.api import router

app = FastAPI()
app.include_router(router)

# Expose specific agent endpoints as tools
mcp = FastApiMCP(app, include_tags=["agents"])
mcp.mount() # Mounts at /mcp
```

#### 2. Agent-to-Tool Mapping
We need to ensure our Agno agents are reachable via FastAPI routes so `fastapi-mcp` can pick them up.
*   **Route:** `POST /agents/{agent_name}/run`
*   **Schema:** `RunRequest(prompt: str, context: dict)`
*   **Result:** `RunResponse(response: str, artifacts: list)`

#### 3. Client Configuration Generator
We will create a helper script `generate_config.py`.
*   **Function:** Generates the `claude_desktop_config.json` or `cursor_config.json` needed to connect a local IDE to the running Armada instance.

### Implementation Steps

1.  **Dependency:** Add `fastapi-mcp` to `requirements.txt`.
2.  **API Structure:** Refactor the Armada's entry point to use FastAPI (if not already) and define clear Pydantic models for Agent inputs/outputs.
3.  **Documentation:** Use the `description` fields in FastAPI routes heavily, as these become the "System Prompt" for the LLM calling the tool.

### Refined Workflow: "Cursor + Armada"
1.  **Dev:** Opens Cursor.
2.  **Dev:** Connects Cursor to `http://localhost:8000/mcp`.
3.  **Dev:** Types in Cursor Chat: "Ask the ReconSquad to find the docs for `fastapi-mcp` and summarize them."
4.  **Cursor:** Calls `recon_squad_run(prompt="...")` via MCP.
5.  **Armada:** Executes the squad.
6.  **Cursor:** Displays the summary directly in the IDE.
