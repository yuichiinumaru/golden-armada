# MindsDB MCP Server: The AI Context Protocol

## Synthesis
The `mindsdb-minds-mcp` repo is a reference implementation of an MCP server for MindsDB. It uses `mcp.server.fastmcp` (a Python framework similar to FastAPI but for MCP) to expose MindsDB's "Minds" as resources and tools.

**Key Components:**
*   **Resources:**
    *   `minds://{api_key}`: Lists all available AI "Minds".
    *   `minds://{mind_name}/{api_key}`: Gets details of a specific Mind.
*   **Tools:**
    *   `completion(mind_name, message, api_key)`: The core tool. It delegates the thinking to a MindsDB "Mind" (which might be wrapping GPT-4, Claude, or a fine-tuned model).
*   **FastMCP:** A very clean, decorator-based way to define MCP servers (`@mcp.resource`, `@mcp.tool`).

## Strategic Ideas for Golden Armada
This implementation reinforces the "Agent-as-a-Service" pattern. Instead of embedding the LLM logic directly into the client (the IDE), it offloads it to a server (MindsDB) via a standard protocol (MCP).

1.  **FastMCP for Golden Armada:** We should adopt `FastMCP` (or a similar lightweight Python wrapper) for our own `golden-armada-mcp` server. It dramatically reduces boilerplate compared to raw stdio/SSE handling.
2.  **The "Mind" Abstraction:** MindsDB treats an AI model + Data Source + Prompt Template as a single addressable entity called a "Mind". We should replicate this.
    *   *SurrealDB Table:* `agents` (or `minds`).
    *   *Columns:* `name`, `model`, `system_prompt`, `tools` (list of tool names).
    *   *MCP Resource:* `golden://agents` -> Lists configured agents.
3.  **Universal Completion Tool:** Instead of exposing 50 different tools to the IDE, we expose *one* meta-tool: `delegate_task(agent_name, task)`.
    *   The IDE (Cursor) says: "I need to fix a bug." -> Calls `delegate_task("BugFixerSquad", "Fix the NPE in line 50")`.
    *   The MCP Server receives this, looks up "BugFixerSquad" in SurrealDB, instantiates the Agno agent with the correct tools, and runs it.

## Integration Plan (Agno + SurrealDB + Gemini 3)

### 1. The `GoldenMCP` Server
We will build a single entry point for all IDE interactions.

```python
from mcp.server.fastmcp import FastMCP
from agno.agent import Agent
from golden_armada.db import SurrealDB

mcp = FastMCP("Golden Armada")

@mcp.tool()
async def assign_task(squad_name: str, instruction: str):
    """Delegates a complex task to a specialized squad of agents."""
    # 1. Fetch Squad config from SurrealDB
    squad_config = await db.get("squads", squad_name)

    # 2. Initialize Agno Agent
    agent = Agent(
        role=squad_config.role,
        model=Gemini3(id=squad_config.model),
        tools=load_tools(squad_config.tools)
    )

    # 3. Execute
    response = await agent.run(instruction)
    return response.content
```

### 2. Dynamic Resource Discovery
We will expose the state of the Armada as MCP Resources.
*   `armada://squads`: List of active squads.
*   `armada://memory/recent`: Recent learnings stored in SurrealDB.
*   `armada://logs/error`: Recent error logs from the swarm.

### 3. Why this is powerful?
It turns the IDE into a **Command and Control Center** for the swarm. The developer doesn't write the code; they direct the squads that write the code.
