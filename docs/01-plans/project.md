# CodeSwarm: Project Specifications

## 1. Overall Project Goal
To implement a multi-agent coding system ("CodeSwarm") focusing on collaborative code generation, review, and project management using the **Agno framework** (formerly Phidata). The project has migrated from Google ADK to Agno to leverage its agentic capabilities and cleaner abstraction.

## 2. Architectural Choices (Agno-based)
CodeSwarm leverages the Agno framework to achieve:
*   **Agent Orchestration:** Flexible management of Planner, Admin, Knowledge, Developer, and Revisor agents.
*   **Structured Outputs:** Uses Pydantic models for reliable communication between agents and the system.
*   **Tool Integration:** Python function-based tools for file operations, web access, code execution, and MCP communication.

## 3. Core System Components

### 3.1. Agent Roles and Responsibilities

*   **PlannerAgent (Strategic Planner):**
    *   **Responsibilities:** Analyzes the overall project goal and state to produce a high-level strategy and roadmap (updates `todo.md`).
    *   **Role:** The "Brain" ensuring long-term coherence.
*   **AdminAgent (Task Manager):**
    *   **Responsibilities:** Translates the strategic plan into specific, atomic `TaskAssignment`s for the current round.
    *   **Output:** Structured JSON via `AdminTaskOutput`.
*   **KnowledgeAgent (Context Provider):**
    *   **Responsibilities:** Performs RAG (Retrieval-Augmented Generation) style searches over the codebase to provide relevant context (patterns, imports) to the DevAgent before execution.
*   **DevAgent (Software Developer):**
    *   **Responsibilities:** Executes coding tasks, creates/edits files, and self-verifies code using execution tools.
    *   **Output:** Structured JSON via `DevAgentOutput`.
*   **RevisorAgent (QA & Code Reviewer):**
    *   **Responsibilities:** rigorous critique of code against requirements. Provides actionable feedback for the feedback loop.
    *   **Output:** Structured JSON via `RevisorAgentOutput`.
*   **AdminLoggerAgent:**
    *   **Responsibilities:** Updates `docs/changelog.log` and `docs/tasklist.md`.

### 3.2. Orchestration Logic (`codeswarm/agent_os.py`)

The `AgentOS` follows a dynamic "OODA" style loop:
1.  **Strategic Planning Phase:** `PlannerAgent` assesses the state and updates the strategic plan.
2.  **Task Assignment Phase:** `AdminAgent` generates atomic tasks based on the strategy.
3.  **Execution Phase:**
    *   **Knowledge Retrieval:** `KnowledgeAgent` fetches context for each task.
    *   **Dev/Revisor Loop:** Tasks are executed in parallel. Each task undergoes an iterative feedback loop (Dev -> Revisor -> Feedback -> Dev) until approved or max retries reached.
    *   **Event Logging:** All actions are logged structurally to `codeswarm_events.jsonl`.
4.  **Logging Phase:** `AdminLoggerAgent` updates documentation.
5.  **State Persistence:** Session state and TaskTree are saved to `codeswarm_state.json` after each phase for resilience.

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
