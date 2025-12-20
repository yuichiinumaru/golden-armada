# Terminal MCP Server Analysis

## 1. Synthesis: Terminal MCP
This repository (`weidwonder/terminal-mcp-server`) is a straightforward **Model Context Protocol (MCP) Server** designed to give LLMs direct access to a shell (Terminal).

### Core Features:
1.  **Local & Remote Execution**: It supports running commands on the local machine *or* on remote servers via SSH (`host` parameter).
2.  **Session Persistence**: It maintains a persistent shell session (reusing the same environment) for up to 20 minutes. This is critical for tasks like:
    *   `cd /path/to/repo` -> `npm install` -> `npm test` (The directory change persists).
    *   Activating a virtual environment (`source venv/bin/activate`) and then running python scripts.
3.  **Environment Variables**: Allows injecting custom ENV vars per command or session.
4.  **SSH Key Auth**: Uses the standard `~/.ssh/id_rsa` for authentication, making it easy to integrate with existing devops workflows.
5.  **Stdio & SSE**: Supports both standard input/output (for local local LLM apps like Claude Desktop) and Server-Sent Events (for remote/http access).

### Tool Definition
It exposes a single, powerful tool: `execute_command`.
*   **Parameters**: `command`, `host` (optional), `username` (optional), `session` (optional), `env` (optional).
*   **Return**: `stdout` and `stderr`.

## 2. Strategic & Architectural Ideas for Golden Armada

### A. The "Remote Dev Server" Pattern
Instead of running code directly on the machine hosting the Golden Armada (which might be a production container or a limited sandbox), we can use this MCP server to control a **Dedicated Dev Environment**.
*   **Architecture**:
    *   **Golden Armada (Brain)**: Runs in a secure, stable environment.
    *   **Terminal MCP (Hands)**: Connects to a throwaway Docker container or a cloud VM via SSH.
    *   **Benefit**: If the agent runs `rm -rf /`, it destroys the dev sandbox, not the Armada itself.

### B. Persistent Sessions for Complex Tasks
The `session` feature is a game-changer for autonomous coding.
*   **Scenario**: "Refactor this React component."
*   **Workflow**:
    1.  `execute_command(cmd="cd frontend", session="refactor-1")`
    2.  `execute_command(cmd="npm test Button.test.js", session="refactor-1")` -> Fails.
    3.  `execute_command(cmd="npm install missing-dep", session="refactor-1")` -> Works.
    4.  `execute_command(cmd="npm test Button.test.js", session="refactor-1")` -> Passes.
*   **Insight**: Stateless command execution (like Python's `subprocess.run` in a loop) is painful because you lose directory context (`cwd`) and env vars between steps. This MCP server solves that.

### C. Multi-Host Orchestration
A single agent could control multiple servers by swapping the `host` parameter.
*   **DevOps Squad**: Could deploy code to `staging.server.com` and `prod.server.com` simultaneously using the same tool interface.

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

To integrate this into the Golden Armada:

### Step 1: Deploy Terminal MCP as a Sidecar
Deploy the `terminal-mcp-server` as a Docker container alongside the Golden Armada.
*   **Connection**: The Armada connects via SSE (`http://terminal-mcp:8080/sse`) or Stdio if running locally.

### Step 2: The "SysAdmin" Tool
Wrap the MCP client in an Agno Tool.
*   **Tool**: `shell_exec(command: str, session_id: str = "default", remote_host: str = None)`
*   **Logic**: Delegates to the MCP client.

### Step 3: SurrealDB Session Tracking
Store active session IDs in SurrealDB to allow agents to "resume" work after a sleep cycle.
*   **Schema**:
    ```sql
    DEFINE TABLE shell_session SCHEMAFULL;
    DEFINE FIELD session_id ON TABLE shell_session TYPE string;
    DEFINE FIELD host ON TABLE shell_session TYPE string;
    DEFINE FIELD last_active ON TABLE shell_session TYPE datetime;
    DEFINE FIELD working_dir ON TABLE shell_session TYPE string; -- Tracked manually via 'pwd'
    ```

### Step 4: Security Guardrails
Since `execute_command` is dangerous:
1.  **Sandboxing**: Ensure the SSH target is a confined environment (Docker container).
2.  **Command Allowlist/Blocklist**: Implement a middleware in the Armada's MCP client that blocks dangerous commands (`rm -rf /`, `mkfs`, etc.) or requires human approval for them.

### Summary
The `terminal-mcp-server` is the "Hands" of the Golden Armada. It provides the **persistent, stateful shell access** required for real software engineering tasks (installing deps, running servers, testing), decoupled from the agent's runtime environment via SSH/MCP.
