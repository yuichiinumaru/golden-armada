# CodeSwarm: Project Specifications

## 1. Overall Project Goal
To implement a multi-agent coding system ("CodeSwarm") focusing on collaborative code generation, review, and project management using the **Agno framework** (formerly Phidata). The project has migrated from Google ADK to Agno to leverage its agentic capabilities and cleaner abstraction.

## 2. Architectural Choices (Agno-based)
CodeSwarm leverages the Agno framework to achieve:
*   **Agent Orchestration:** Flexible management of Admin, Developer, and Revisor agents.
*   **Structured Outputs:** Uses Pydantic models for reliable communication between agents and the system.
*   **Tool Integration:** Python function-based tools for file operations, web access, and code execution.

## 3. Core System Components

### 3.1. Agent Roles and Responsibilities

*   **AdminAgent (Project Manager):**
    *   **Responsibilities:** Defines project scope, breaks down goals into tasks, and manages the project log.
    *   **Output:** Structured JSON via `AdminTaskOutput`.
*   **DevAgent (Software Developer):**
    *   **Responsibilities:** Executes coding tasks, creates/edits files.
    *   **Output:** Structured JSON via `DevAgentOutput`.
*   **RevisorAgent (Code Reviewer):**
    *   **Responsibilities:** Reviews code against requirements and best practices.
    *   **Output:** Structured JSON via `RevisorAgentOutput`.
*   **AdminLoggerAgent:**
    *   **Responsibilities:** Updates `docs/changelog.log` and `docs/tasklist.md`.

### 3.2. Orchestration Logic (`codeswarm/agent_os.py`)

*   The `AgentOS` class orchestrates the workflow:
    1.  **Planning Phase:** AdminAgent generates tasks based on the goal and current state.
    2.  **Execution Phase:** Dev/Revisor pairs execute the tasks in parallel (using `concurrent.futures`).
    3.  **Logging Phase:** AdminLoggerAgent updates project documentation.

### 3.3. Tool Abstractions (`codeswarm/tools.py`)
*   Tools are defined as standalone Python functions (e.g., `read_file`, `write_file`, `execute_python_code`) and passed to Agno agents.

## 4. Environment and Configuration
*   **Python Environment:** Requires `agno`, `google-genai`, `python-dotenv`, `beautifulsoup4`, `requests`.
*   **Configuration:** Managed by `codeswarm/config.py` using `.env`.
*   **Execution:** Run as a module: `python -m codeswarm.main` from the project root.

---
## Legacy Architecture (Google ADK)
*The previous implementation using Google ADK is archived in `archive/codeswarm_legacy/`. The following documentation is preserved for historical context.*

### [Legacy] Architectural Choices for CodeSwarm using ADK
CodeSwarm previously leveraged Google's Agent Development Kit (ADK). This implementation focused on `LlmAgent`, `FunctionTool`, and `InMemorySessionService`.

### [Legacy] Core System Components (ADK-based)
*   **AdminAgent:** Used `AdminTaskOutput` and ADK tools.
*   **DevAgent:** Used `DevAgentOutput` and ADK-native tool calling.
*   **RevisorAgent:** Used `RevisorAgentOutput`.
*   **Orchestration:** Managed by `main_adk_controller.py`.
