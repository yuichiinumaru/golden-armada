# MCP Code Executor: Secure Python Sandbox

## 1. Synthesis

**Repository:** `bazinga012/mcp_code_executor`
**Language:** TypeScript (Node.js)
**Core Purpose:** An MCP server that provides a sandboxed environment for LLMs to write, manage, and execute Python code. It bridges the gap between generating code and running it, with support for persistence and environment management.

### Key Capabilities
*   **Sandbox Execution:** Runs Python code within strictly defined environments (Conda, `venv`, or `uv`).
*   **Incremental Development:** Solves the context window limit by allowing agents to:
    1.  `initialize_code_file`: Create a file.
    2.  `append_to_code_file`: Add functions/classes iteratively.
    3.  `read_code_file`: Verify content.
    4.  `execute_code_file`: Run the final artifact.
*   **Dependency Management:** Tools to `install_dependencies` and `check_installed_packages` dynamically, ensuring the runtime matches the code's requirements.
*   **Dynamic Configuration:** Can switch execution environments on the fly (e.g., swapping from a Data Science conda env to a Web Dev venv).

### Architectural Highlights
*   **Storage Isolation:** Uses a dedicated `CODE_STORAGE_DIR` to contain all generated artifacts.
*   **Process wrapping:** Wraps system calls (`exec`) to handle Python execution, capturing `stdout` and `stderr` to return to the LLM.
*   **Platform Agnostic:** Supports Windows and POSIX pathing and shell commands.

---

## 2. Strategic Ideas for Golden Armada

The Golden Armada's "Coding Squad" needs to do more than just *print* code blocks; it needs to *test* and *run* them. This repo provides the blueprint for that capability.

### A. The "DevServer" Pattern
Instead of running code on the user's local machine directly, we treat the MCP Code Executor as a "Remote DevServer".
*   **Idea:** Run this MCP server in a Docker container with pre-installed heavy dependencies (PyTorch, Pandas, SurrealDB drivers).
*   **Benefit:** Keeps the "Golden Armada" lightweight. The core logic runs locally, but heavy computation happens in the isolated container.

### B. Persistent Memory for Code
The `initialize` -> `append` -> `execute` flow is a primitive form of file system management.
*   **Idea:** Enhance this into a "Project Manager". Instead of just temp files, map the `CODE_STORAGE_DIR` to a real project structure.
*   **Strategy:** When the Coding Squad works on a feature, it writes actual files to disk, runs tests via `execute_code_file`, and if successful, commits them to git.

### C. Self-Healing Environments
The `install_dependencies` tool allows the agent to fix its own environment errors.
*   **Idea:** If an agent gets a `ModuleNotFoundError`, it should be trained to automatically call `install_dependencies` for the missing package and retry execution.

---

## 3. Integration Plan (Agno + SurrealDB + Gemini 3)

We will integrate this as the primary "Hand" for the `CodingSquad` and `DataAnalysisSquad`.

### Component: `ExecutionService` (MCP)

#### 1. Integration with Agno Tools
We will register the MCP tools directly into Agno's `Toolkit`.

```python
# Conceptual Agno Integration
from agno.agent import Agent
from agno.tools.mcp import MCPTool

code_executor = MCPTool(
    server_url="http://localhost:8000", # Or usage of the stdio transport
    tools=["execute_code", "install_dependencies", "execute_code_file"]
)

data_scientist = Agent(
    role="Data Scientist",
    tools=[code_executor],
    instructions="Write code to analyze the data. If libraries are missing, install them."
)
```

#### 2. The "Workspace" Abstraction
We need to map `CODE_STORAGE_DIR` to the User's project root (or a safe subdirectory).
*   **Config:** When starting the Golden Armada, the user defines `PROJECT_ROOT`. The MCP server is launched with `CODE_STORAGE_DIR=$PROJECT_ROOT`.
*   **Safety:** We must ensure the MCP server cannot traverse *up* from this directory (e.g., `../`). The repo already implements some checks, but we should enforce strict Docker volume mounting.

#### 3. SurrealDB Logging
Every execution should be logged to SurrealDB for audit and debugging.
*   **Flow:**
    1.  Agent calls `execute_code`.
    2.  MCP runs code.
    3.  Agent receives output.
    4.  Agent (or a middleware wrapper) logs to SurrealDB:
        ```sql
        CREATE execution_log SET
            agent = 'coding_squad',
            code_snippet = "print('hello')",
            output = "hello",
            exit_code = 0,
            timestamp = time::now();
        ```

### Implementation Steps

1.  **Containerize:** Use the provided `Dockerfile` as a base. Add `surrealdb` client libraries to the base image so agents can interact with the Armada's memory natively.
2.  **Tool Wrapping:** Create a Python wrapper class `RemotePythonExecutor` in the codebase that acts as the client for this MCP server.
3.  **Error Handling Policy:** Implement a "Retry Loop" in the `CodingSquad` system prompt:
    *   *If execution fails:* Read `stderr`.
    *   *If dependency error:* Call `install_dependencies`.
    *   *If syntax error:* Rewrite code.
    *   *If logic error:* Add print statements and `execute_code` again.

### Refined Workflow: The "Test-Driven Generation" Loop
1.  **User:** "Create a function to calculate Fibonacci."
2.  **Coding Agent:**
    *   Calls `initialize_code_file(filename="test_fib.py", content="import unittest...")` (Writes the test first).
    *   Calls `initialize_code_file(filename="fib.py", content="def fib(n): pass")`.
    *   Calls `execute_code_file("test_fib.py")` -> **FAILS**.
3.  **Coding Agent:**
    *   Calls `overwrite_file("fib.py", ...)` (Implements logic).
    *   Calls `execute_code_file("test_fib.py")` -> **PASSES**.
4.  **Result:** High-confidence code generation verified by actual execution.
