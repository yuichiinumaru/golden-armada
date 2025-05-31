# CodeSwarm: Project Specifications

## 1. Overall Project Goal
To implement a multi-agent coding system ("CodeSwarm") focusing on collaborative code generation, review, and project management using the Google Agent Development Kit (ADK). The system features Admin, Developer, and Revisor agents that interact to fulfill user-defined coding and project analysis goals. All operations, especially file I/O and API calls, must be real and executable.

## 2. Architectural Choices for CodeSwarm using ADK
CodeSwarm leverages Google's Agent Development Kit (ADK) to achieve:
*   **Error Transparency:** Clearer diagnosis of issues when interacting with Gemini API.
*   **Control over Interactions:** Direct management of agent-LLM interactions, prompts, and data handling.
*   **Robustness:** Foundation for complex agent behaviors, task decomposition, and error recovery.

The ADK provides a more direct interface to Gemini models, facilitating a robust and debuggable system.

## 3. Core System Components (ADK-based)

### 3.1. Agent Roles and Responsibilities

Agents are implemented using ADK's `LlmAgent` (specifically tested with `google-adk==1.1.1`). Input grounding for agents heavily relies on `session.state`.

*   **AdminAgent (Project Manager):**
    *   **Responsibilities:**
        *   Understands the overall project goal and `target_project_path` (via `session.state`).
        *   Defines project scope and breaks down complex goals into a sequence of smaller, actionable tasks. This may involve a two-step internal process:
            1.  **Interpreter (Cognitive):** Understands input, generates task content in natural language. (Tool-less, `tools_override=[]`).
            2.  **Formatter (Structuring):** Takes natural language and structures it into the required JSON output format for the orchestrator. (Tool-less, `tools_override=[]`).
        *   Outputs a list of tasks in a structured JSON format. Due to ADK 1.1.1 limitations with `output_model` for tool dispatch and `response_mime_type` conflicts with tools, this JSON is typically generated in the agent's text response and parsed by the orchestrator.
        *   Prompts must be precise for reliable JSON. Paths in tasks should be relative to the project root.
        *   Receives summaries of Dev work and Revisor feedback to inform subsequent rounds (if applicable).
    *   **AdminLoggerAgent (Specialized Admin Task):** A dedicated agent responsible for logging.
        *   Updates `project_logs/changelog.log` (and potentially `project_logs/tasklist.md` in future iterations) using its file I/O tools. Tool calls may be ADK-native or orchestrator-managed.
    *   **Tools (for AdminLoggerAgent):** File I/O (`write_file`). Admin Interpreter/Formatter are tool-less.

*   **DevAgent (Software Developer - Template for X instances):**
    *   **Responsibilities:**
        *   Receives a specific coding/processing task (e.g., `create_or_update_file`, `execute_python_script`) from the orchestrator.
        *   Critical inputs like target file paths are provided via `session.state`.
        *   Generates code or text content.
        *   Requests tool calls (e.g., `write_file`) by outputting a specific JSON structure (e.g., `{"function_call": {"name": "tool_name", "args": {...}}}`) in its text response.
        *   The orchestrator parses this JSON and executes the actual tool from `tool_logic.py`.
    *   **Tools (Invoked by Orchestrator based on DevAgent's output):** File I/O (`write_file`, `read_file`), potentially script execution (`execute_python_code` with user confirmation).

*   **RevisorAgent (Code/Content Reviewer - Template for X instances):**
    *   **Responsibilities:**
        *   Receives a file path (via `session.state`) and review instructions.
        *   Uses tools to read the file. May also consult documentation via web browsing tools if necessary.
        *   Reviews for correctness, adherence to instructions, standards, etc.
        *   Generates specific, constructive feedback.
        *   ADK's native tool calling mechanism is generally effective for this agent.
    *   **Tools:** File I/O (`read_file`), Web Browsing (`fetch_web_page_text_content`).

### 3.2. Orchestration Logic (`main_adk_controller.py`)

*   The central controller script manages the workflow:
    1.  User provides initial goal, `target_project_path`, number of agent pairs (X), and rounds.
    2.  Orchestrator initializes AdminAgent (Interpreter/Formatter), X DevAgents, X RevisorAgents, and AdminLoggerAgent. It manages `session.state` for contextual data.
    3.  **Round-Based Workflow:**
        *   **Admin - Task Definition:** Orchestrator invokes AdminAgent (Interpreter then Formatter) with the goal and project context (via `session.state`). Admin returns a list of structured tasks (JSON).
        *   **Task Execution Loop:** Orchestrator iterates through the task list. For each task:
            *   **Dev Phase:** Passes task details to DevAgent_i (using `session.state` for paths, etc.). DevAgent_i generates content and requests tool calls (e.g., `write_file`) via structured JSON in its response. Orchestrator parses this and executes the tool.
            *   **Revisor Phase:** If applicable, orchestrator passes the path of the file modified/created by DevAgent_i to RevisorAgent_i (via `session.state`). RevisorAgent_i reviews and returns feedback.
        *   **Admin - Logging:** After all tasks in a round (or periodically), orchestrator invokes AdminLoggerAgent to update `project_logs/changelog.log` with a summary.
    4.  The system can loop for multiple rounds if designed for iterative development.
    5.  User confirmation is implemented in the orchestrator for potentially dangerous tools requested by agents (e.g., script execution).

### 3.3. Tool Abstractions (`tool_logic.py`)
*   Tool functions are defined in `tool_logic.py` and wrapped by ADK `FunctionTool` for agents that use ADK-native dispatch (like Revisor).
*   For orchestrator-managed calls (like for DevAgent), the orchestrator calls functions from `tool_logic.py` directly.
*   **Path Safety:**
    *   Tools expect absolute paths, resolved by the orchestrator.
    *   Admin agents are prompted to output relative paths.
    *   A `TARGET_PROJECT_PATH_FOR_TOOLS` environment variable is used as a secure base path.
    *   Rogue absolute paths from LLMs are handled by using only their basename against this secure base path.
*   **Tool Error Reporting:** Tools return simple dictionaries (e.g., `{'status': 'success', ...}` or `{'status': 'error', ...}`) to the caller (agent or orchestrator).

## 4. Key Design Considerations

### 4.1. Input Grounding, Output Parsing, and Memory
*   **LLM Input Grounding:** Critically relies on `session.state`. Complex data passed as single JSON strings in prompts is unreliable. Key parameters are set in `session.state` by the orchestrator and referenced in agent prompts via templating.
*   **LLM Output Formatting (JSON):** Requires precise, directive prompting. For complex JSON (like AdminAgent's task list), a two-step internal agent process (content generation then formatting) is more robust. JSON in agent responses is often parsed from text by the orchestrator.
*   **Memory:** `session.state` provides short-term memory within a round. Longer-term "memory" or context is managed via files in `target_project_path` (e.g., code files, intermediate outputs) and by consulting `project_logs/changelog.log` for history. The AdminAgent's task breakdown strategy is key for handling large projects.

### 4.2. API Key Management
*   The system loads the `GEMINI_API_KEY` from a `.env` file. ADK typically uses this via the `GOOGLE_API_KEY` environment variable.

### 4.3. Prompt Engineering
*   Prompts are stored in external JSON files (e.g., `prompts/admin_prompt.json`).
*   Prompts must be explicit, direct, and sometimes redundant. ALL CAPS can be used for emphasis on critical instructions.
*   Clearly distinguish between instructions for *output format* and *how to derive content*.
*   For agents intended to request tool calls via JSON output (like DevAgent), prompts must clearly state that their *entire response* (or a clearly demarcated part) should be the JSON for the function call.

### 4.4. Error Handling and Debugging
*   The orchestration layer catches errors from ADK agent steps or tool executions.
*   **Debugging Techniques:**
    *   Log raw LLM inputs and outputs.
    *   A centralized wrapper function for agent execution can manage logging and parsing.
    *   Add detailed debug prints within tool logic.
    *   Simplify inputs and test agents in isolation when troubleshooting.
*   ADK 1.1.1 uses function-based callbacks (e.g., `before_model_callback`) for observing agent lifecycle events.

## 5. Environment and Configuration
*   **Python Environment:** Requires `google-genai`, `google-adk[extensions]==1.1.1` (or version used), `python-dotenv`. `requests` and `beautifulsoup4` are needed for web browsing tools.
*   **`.env` File:** Manages `GEMINI_API_KEY`, model names (e.g., `ADMIN_MODEL`, `DEV_MODEL`, `REVISOR_MODEL`), `DEFAULT_PROJECT_PATH`, `DEFAULT_GOAL`, `DEFAULT_PAIRS`, `DEFAULT_ROUNDS`, and `TARGET_PROJECT_PATH_FOR_TOOLS`.
*   **Directory Structure:** Key directories include `codeswarm/` (main package), `generated_code/` (default output), `project_logs/` (for `changelog.log`, `tasklist.md`).
*   **Execution:** Run as a module: `python -m codeswarm.main_adk_controller` from the parent directory of `codeswarm/`.

## 6. Key Learnings and ADK Specifics (primarily for `google-adk==1.1.1`)

This section consolidates practical learnings from CodeSwarm development:

*   **ADK Version and Model Compatibility:**
    *   `google-adk==1.1.1` was used. `gemini-1.5-flash-latest` proved compatible, while other models (e.g., `gemini-pro`) sometimes caused 404 errors due to ADK 1.1.1 potentially targeting an older API endpoint.
*   **`LlmAgent` Configuration (ADK 1.1.1):**
    *   `output_model` for Pydantic model parsing for tool dispatch was problematic (Pydantic validation errors). More suited for parsing responses into data models if the LLM outputs matching JSON.
    *   `response_mime_type: "application/json"` in `generation_config` conflicts with tool usage.
*   **Tool Usage and Dispatch:**
    *   **Granular Tasks:** AdminAgent should break down goals into small, specific tasks for reliability.
    *   **Orchestrator-Managed Tool Calls:** For DevAgent, the orchestrator parses `function_call` JSON from the agent's text response and executes the tool. This is more robust for complex actions or tools not directly in the agent's ADK tool list.
    *   **ADK-Native Tool Calls:** Effective for simpler agents like RevisorAgent and potentially AdminLoggerAgent, given clear prompts and tool definitions.
    *   **Cognitive Tasks:** Use `tools_override=[]` for agents not needing tools.
*   **Path Handling:**
    *   Admin outputs relative paths; orchestrator converts to absolute using `target_project_path`.
    *   Tools use `TARGET_PROJECT_PATH_FOR_TOOLS` and handle rogue absolute paths by using only the basename.
*   **Session Management (ADK 1.1.1):**
    *   `InMemorySessionService` is used. Ensure the same service instance is used for session creation and `Runner`.
    *   Consistent `user_id` is crucial.
    *   `session.state` is vital for passing contextual data (project goals, file paths) between orchestrator and agents, and for input grounding in prompts.
*   **Asynchronous Operations:** Core ADK operations (`create_session`, `runner.run_async`) are `async` and require `await`.
*   **Import Paths & Callbacks (ADK 1.1.1):**
    *   Use official ADK import paths (e.g., `google.adk.events.Event`, `google.adk.sessions.InMemorySessionService`).
    *   Callbacks are function-based (e.g., `before_model_callback`), using `CallbackContext` and `ToolContext`.
*   **Project Documentation:**
    *   Ongoing tasks and progress are tracked in `docs/tasklist.md`.
    *   Historical changes and round summaries are logged in `project_logs/changelog.log`. (Note: `docs/changelog.log` was mentioned in `jules-notes.md` but `project_logs/changelog.log` is the operational one from recent dev.)

This document provides a blueprint for CodeSwarm. Detailed designs evolve with ongoing implementation and testing. For a detailed evolution and specific debugging notes, see `docs/codeswarm_development_evolution.md`.