# AgentOS Resources

## 🛠️ Tools (Agno)
- `CalculatorTools`: Basic math operations.
- `DuckDuckGoTools`: Web search.
- `FileTools`: File system operations.
- `ShellTools`: Execute shell commands (Use with caution).
- `PythonTools`: Execute Python code.

## 🔌 MCP Servers (Model Context Protocol)
- `mcp-server`: Local MCP server running on port 8000.
  - Provides access to local tools and data.
  - Integration via `agno.tools.mcp.McpTools`.

## 🗄️ Databases
- **SurrealDB** (`vivi-surrealdb:8000`)
  - **Usage:** Agent Memory (Khala), Structured Data.
  - **Access:** `khala.infrastructure.surrealdb.client.SurrealDBClient`.
  - **Credentials:** `root` / `surrealdb_secret_password`.

- **FalkorDB** (`vivi-falkordb:6379`)
  - **Usage:** Knowledge Graph, Relationships.
  - **Access:** Redis client or FalkorDB specific client.
  - **Password:** `falkordb`.

- **Redis** (`redis:6379`)
  - **Usage:** Caching, Pub/Sub, Task Queues.
  - **Access:** Standard Redis client.

## 🧠 Models
- `gemini-2.5-flash`: Fast, efficient, good for general tasks.
- `gemini-2.5-pro`: High reasoning, good for complex tasks.
- `gemini-1.5-flash`: (Legacy/Fallback)
