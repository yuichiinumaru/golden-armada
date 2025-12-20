# Reference Analysis: MCP Code Executor

## 1. Synthesis

**MCP Code Executor** is a Model Context Protocol (MCP) server designed to give Large Language Models (LLMs) the ability to execute Python code in a safe, sandboxed environment. It acts as a bridge between the LLM and a runtime environment (Conda, Virtualenv, or UV), allowing the model to write code, install dependencies, run scripts, and see the output.

### Core Value Proposition
This project solves the "execution gap" for LLMs. While LLMs can write code, they cannot typically run it to verify correctness, perform calculations, or process data. MCP Code Executor provides a standardized interface for this, supporting:
1.  **Code Execution**: Running Python snippets.
2.  **State Management**: Maintaining files across execution calls (incremental coding).
3.  **Environment Management**: Installing packages and configuring the runtime.

### Key Features
*   **Sandboxed Environments**: Supports Conda, standard `venv`, and `uv` (a fast Python package installer and resolver).
*   **Incremental Code Generation**: Addresses the token limit problem by allowing the LLM to build a file step-by-step (`initialize_code_file` -> `append_to_code_file` -> `execute_code_file`).
*   **Dependency Management**: Tools to `install_dependencies` and `check_installed_packages`.
*   **Dynamic Configuration**: The environment can be switched at runtime.
*   **MCP Standard**: Built on the Model Context Protocol, making it plug-and-play with MCP-compliant clients (like Claude Desktop or custom agents).

### Architectural Components
The codebase is a TypeScript/Node.js application (`src/index.ts`) that wrappers Python execution.
*   **MCP Server**: Uses `@modelcontextprotocol/sdk` to define tools and handle requests.
*   **Tool Handlers**:
    *   `execute_code`: Writes code to a temp file and runs `python -u file.py`.
    *   `initialize/append/read_code_file`: File system operations to manage persistent scripts in `CODE_STORAGE_DIR`.
    *   `install_dependencies`: Maps to `pip install`, `conda install`, or `uv pip install`.
*   **Environment Abstraction**: A switch statement in `getPlatformSpecificCommand` handles the nuances of activating different environment types on Windows/Linux.
*   **Docker Support**: Includes a Dockerfile for containerized deployment.

---

## 2. Strategic & Architectural Ideas for CodeSwarm

**CodeSwarm** (Agno + SurrealDB + Gemini 3) aims to be an autonomous software development system. The ability to *execute* the code it writes is fundamental to moving from "Drafting" to "Engineering".

### 2.1. The "Sandbox" Pattern
The CodeSwarm agents currently generate code files. To verify them, they need a sandbox.
*   **Idea**: Implement a `CodeExecutionTool` in Agno that mimics the logic of this MCP server but integrated directly into the CodeSwarm infrastructure.
*   **Application**: Before a `DevAgent` marks a task as complete, it *must* write a test, execute it using this tool, and only proceed if the test passes.
*   **Security**: The use of Docker in the reference repo is crucial. CodeSwarm should ideally spawn ephemeral Docker containers for execution to prevent agents from accidentally damaging the host system.

### 2.2. Incremental File Editing
The reference repo's `append_to_code_file` is a primitive form of editing.
*   **Idea**: Enhance this for CodeSwarm. Agents need to *patch* files, not just append.
*   **Refinement**: We should provide tools like `apply_patch` (diff-based) or `replace_block` (search/replace) which are more suitable for software maintenance than simple appending.

### 2.3. Environment Awareness
The reference repo explicitly manages Conda/Venv.
*   **Idea**: CodeSwarm agents should be "Environment Aware".
*   **Application**: An agent starting a Django project should know to create a virtualenv, install `requirements.txt`, and run `manage.py migrate`. The `install_dependencies` tool is a good primitive to expose.

### 2.4. MCP Integration
Since CodeSwarm is moving to Agno (which supports tool calling), we could simply *use* this MCP server as an external service rather than rewriting it.
*   **Strategy**: If CodeSwarm is designed to be extensible, we can treat "Code Execution" as a pluggable MCP capability.
*   **Benefit**: This decouples the "Brain" (CodeSwarm Agents) from the "Hands" (Execution Environment).

---

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

We will integrate code execution capabilities into CodeSwarm to enable Test-Driven Development (TDD) loops for agents.

### 3.1. Stack Mapping

| Component | MCP Code Executor | CodeSwarm Target | Notes |
| :--- | :--- | :--- | :--- |
| **Interface** | MCP (JSON-RPC) | **Agno Toolkit** | We can wrap the logic in a Python class `CodeExecutorToolkit`. |
| **Runtime** | Local Python/Docker | **Docker (via Python SDK)** | Use `docker-py` to spawn sandboxes. |
| **Storage** | Local Filesystem | **SurrealDB + Volume** | Store execution logs in DB, files in shared volume. |
| **Logic** | TypeScript | **Python** | Rewrite the simple execution logic in Python. |

### 3.2. Data Model (SurrealDB)

We should track execution history to allow agents to "learn" from errors.

**Table: `executions`**
```sql
DEFINE TABLE executions SCHEMAFULL;
DEFINE FIELD agent_id ON executions TYPE string;
DEFINE FIELD code ON executions TYPE string;
DEFINE FIELD output ON executions TYPE string;
DEFINE FIELD error ON executions TYPE string;
DEFINE FIELD exit_code ON executions TYPE int;
DEFINE FIELD duration_ms ON executions TYPE int;
DEFINE FIELD timestamp ON executions TYPE datetime DEFAULT time::now();
```

### 3.3. Agno Agent Implementation

We will create a `CodeExecutorToolkit` in Agno that agents can use.

#### Step 1: The Docker Sandbox
Instead of running on the host (dangerous), we use a standard Python container.

```python
import docker
import os
from agno.tools import Toolkit

class DockerSandbox(Toolkit):
    def __init__(self):
        super().__init__(name="docker_sandbox")
        self.client = docker.from_env()
        self.container = self._get_or_create_container()

    def _get_or_create_container(self):
        # Logic to spin up a 'python:3.11' container with a shared volume
        pass

    def execute_python(self, code: str, filename: str = "script.py"):
        """Executes python code in the sandbox."""
        # 1. Write code to shared volume
        # 2. Exec command in container: python /workspace/script.py
        # 3. Return stdout/stderr
        pass

    def install_package(self, package_name: str):
        """Pip installs a package in the sandbox."""
        pass
```

#### Step 2: The Agent (QA Engineer)
A specialized agent responsible for verification.

```python
from agno.agent import Agent
from codeswarm.tools.docker_sandbox import DockerSandbox

qa_agent = Agent(
    role="QA Engineer",
    goal="Verify code correctness by writing and running tests.",
    tools=[DockerSandbox()],
    instructions="""
    1. When given code, write a unit test for it.
    2. Use `execute_python` to run the test.
    3. If it fails, analyze the stderr and fix the code.
    """
)
```

---

## 4. Specific Implementation Steps

### Phase 1: Local Execution Tool
1.  **Create Tool**: `codeswarm/tools/local_python_executor.py`.
    *   Implement `run_code(code: str)`.
    *   *Warning*: Only use this for non-destructive operations initially.
    *   Include dependency installation support (`pip install`).

### Phase 2: Secure Docker Sandbox (Recommended)
2.  **Dependency**: Add `docker` to `requirements.txt`.
3.  **Create Tool**: `codeswarm/tools/docker_executor.py`.
    *   Implement container lifecycle management (start/stop).
    *   Implement `exec_run` wrapper.

### Phase 3: Agent Integration
4.  **Update `DevAgent`**: Give the Developer Agent access to the executor.
    *   Update `AGENTS.md` to reflect that DevAgents *must* verify code.
5.  **Create `TestRunnerAgent`**: A dedicated agent that takes a file path, writes a `pytest` suite, runs it via the executor, and reports results.

### Phase 4: MCP Bridge (Optional)
6.  If we want to use the *actual* `bazinga012/mcp_code_executor` (e.g. if it's running remotely), we can write an Agno Tool that acts as an MCP Client, sending requests to the MCP server. This allows CodeSwarm to offload execution to a specialized server.

## 5. Detailed Logic Breakdown (from Source)

### 5.1. `index.ts` - The Command Router
*   **Environment Detection**: Checks `ENV_TYPE` (conda/venv/uv).
*   **Command Construction**:
    *   Windows vs Unix path handling.
    *   Prefixes commands with activation scripts (e.g., `source venv/bin/activate && python ...`).
*   **`executeCode`**:
    *   Writes string to file.
    *   Spawns child process.
    *   Captures `stdout` and `stderr`.
    *   Returns JSON response.

### 5.2. File Management
*   **`initialize_code_file`**: Writes content to a new file.
*   **`append_to_code_file`**: Uses `fs.appendFile`.
    *   *Critique*: This is brittle for code. Appending to the end of a Python file works for adding functions, but not for modifying imports or classes defined earlier.
    *   *CodeSwarm Improvement*: We should implement `rewrite_file` or AST-based insertion.

## 6. Conclusion

The `mcp_code_executor` repo provides a clean, standard protocol for "AI Code Execution". For CodeSwarm, the capability is essential. We should implement a **Docker-backed Agno Toolkit** that provides the same functionality (`execute`, `install`, `manage_files`) but with stronger isolation and integration into our specific Agent workflow. This transforms CodeSwarm from a text generator into a functioning software engineering loop.
