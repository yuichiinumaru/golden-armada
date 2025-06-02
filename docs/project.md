# CodeSwarm: Project Specifications

## 1. Overall Project Goal
To implement a multi-agent coding system ("CodeSwarm") focusing on collaborative code generation, review, and project management using the Google Agent Development Kit (ADK). The core ADK transition for CodeSwarm is complete, with recent efforts focused on refining agent prompts, enhancing tool interactions, and ensuring robust structured data exchange via Pydantic models. This document details the project specifications for this ADK-based system, featuring Admin, Developer, and Revisor agents that interact to fulfill user-defined coding goals. All operations, especially file I/O and API calls, must be real and executable.

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
        *   Outputs a list of tasks in a structured JSON format. The `AdminAgent` is configured with `output_model=AdminTaskOutput` (from `codeswarm.adk_models`) for its task assignment output, and this Pydantic model is validated by the orchestrator.
        *   Prompts must be precise for reliable JSON. AdminAgent is prompted to construct absolute paths for `file_to_edit_or_create` in its tasks, based on the `target_project_path` provided by the orchestrator (as per the 'PATH CONSTRUCTION CRITICAL RULE' in `admin_prompt.json`).
        *   Receives summaries of Dev work and Revisor feedback to inform subsequent rounds (if applicable).
        *   Handles logging and updates during its "logging_and_updates" phase, as defined in its prompt and orchestrated by `main_adk_controller.py`. This includes updating `docs/changelog.log` and `docs/tasklist.md`.
    *   **Tools (for AdminAgent during logging_and_updates phase):** File I/O (`write_file` via `admin_tools_adk`). The main task assignment phase of AdminAgent is typically tool-less (`tools_override=[]`).

*   **DevAgent (Software Developer - Template for X instances):**
    *   **Responsibilities:**
        *   Receives a specific coding/processing task (e.g., `create_or_update_file`, `execute_python_script`) from the orchestrator. Task details, including the absolute `file_to_edit_or_create`, are provided via `session.state`.
        *   Generates code or text content.
        *   Is assigned `tools=dev_tools_adk` (which includes tools like `write_file`, `read_file`) and uses `output_model=DevAgentOutput`.
        *   Expected to use ADK's native tool calling mechanism for file operations based on its prompt and available tools. Its final output, structured by `DevAgentOutput`, reflects the outcome of these operations (e.g., success message, file path).
    *   **Tools (ADK-native):** File I/O (`write_file`, `read_file` via `dev_tools_adk`), potentially script execution (`execute_python_code` with user confirmation, if added to `dev_tools_adk`).

*   **RevisorAgent (Code/Content Reviewer - Template for X instances):**
    *   **Responsibilities:**
        *   Receives a file path (via `session.state`), review instructions, and focus areas.
        *   Uses tools like `read_file` to inspect the content of the specified file.
        *   Analyzes the code/text against the original development task, review focus areas, and general best practices.
        *   May use tools like `fetch_web_page_text_content` to consult external documentation or standards.
        *   Formulates detailed, constructive `review_comments` and determines an `approved` status. The RevisorAgent does not write or modify code itself.
        *   ADK's native tool calling mechanism is used.
    *   **Tools:** `read_file`, `list_folder_contents`, `fetch_web_page_text_content`, `chunk_file`, `summarize_chunks`. (as defined in `revisor_tools_adk` and `revisor_prompt.json`)

### 3.2. Orchestration Logic (`main_adk_controller.py`)

*   The central controller script manages the workflow:
    1.  User provides initial goal, `target_project_path`, number of agent pairs (X), and rounds.
    2.  Orchestrator initializes AdminAgent, X DevAgents, and X RevisorAgents. It manages `session.state` for contextual data.
    3.  **Round-Based Workflow:**
        *   **Admin - Task Definition:** Orchestrator invokes AdminAgent with the goal and project context (via `session.state`). Admin returns a list of structured tasks (JSON via `AdminTaskOutput`).
        *   **Task Execution Loop:** Orchestrator iterates through the task list. For each task:
            *   **Dev Phase:** Passes task details to DevAgent_i (using `session.state` for paths, etc.). DevAgent_i uses its ADK-native tools (e.g., `write_file`) to perform the task. Its output (via `DevAgentOutput`) confirms the action.
            *   **Revisor Phase:** If applicable, orchestrator passes the path of the file modified/created by DevAgent_i to RevisorAgent_i (via `session.state`). RevisorAgent_i reviews and returns feedback (via `RevisorAgentOutput`).
        *   **Admin - Logging:** After all tasks in a round (or periodically), orchestrator invokes AdminAgent (in its "logging_and_updates" phase) to update `docs/changelog.log` and `docs/tasklist.md` with a summary.
    4.  The system can loop for multiple rounds if designed for iterative development.
    5.  User confirmation is implemented in the orchestrator for potentially dangerous tools requested by agents (e.g., script execution, if such tools are enabled for agents).

### 3.3. Tool Abstractions (`tool_logic.py`)
*   Tool functions are defined in `tool_logic.py` and wrapped by ADK `FunctionTool` (e.g., `admin_tools_adk`, `dev_tools_adk`, `revisor_tools_adk`) for agents that use ADK-native tool dispatch.
*   **Path Safety:** Path safety for code generation (DevAgent) is primarily handled by `main_adk_controller.py`, which validates that the final absolute path for DevAgent operations is within the `target_project_path` set by the user (via CLI `--path`). For AdminAgent's logging operations, path safety relies on the `target_project_path` provided for that phase correctly pointing to the project's root and the agent adhering to its prompt to only modify specific files (`docs/changelog.log`, `docs/tasklist.md`).
*   **Tool Error Reporting:** Tools return simple dictionaries (e.g., `{'status': 'success', ...}` or `{'status': 'error', ...}`) to the caller (agent or orchestrator).

## 4. Key Design Considerations

### 4.1. Input Grounding, Output Parsing, and Memory
*   **LLM Input Grounding:** Critically relies on `session.state`. Complex data passed as single JSON strings in prompts is unreliable. Key parameters are set in `session.state` by the orchestrator and referenced in agent prompts via templating.
*   **LLM Output Formatting (JSON):** Requires precise, directive prompting. For complex JSON (like AdminAgent's task list), a two-step internal agent process (content generation then formatting) is more robust. JSON in agent responses is often parsed from text by the orchestrator.
*   **Memory:** `session.state` provides short-term memory within a round. Longer-term "memory" or context is managed via files in `target_project_path` (e.g., code files, intermediate outputs) and by consulting `docs/changelog.log` and `docs/tasklist.md` for history. The AdminAgent's task breakdown strategy is key for handling large projects.

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
*   **`.env` File:** Manages `GEMINI_API_KEY`, model names (e.g., `ADMIN_MODEL`, `DEV_MODEL`, `REVISOR_MODEL`), and `DEFAULT_PROJECT_PATH`.
*   **Directory Structure:** Key directories include `codeswarm/` (main package), `generated_code/` (default output for projects if specified), and `docs/` (for `changelog.log`, `tasklist.md`). The `project_logs/` directory can be used for other diagnostic or detailed operational logs if needed in the future.
*   **Execution:** Run as a module: `python -m codeswarm.main_adk_controller` from the parent directory of `codeswarm/`.

## 6. Key Learnings and ADK Specifics (primarily for `google-adk==1.1.1`)

This section consolidates practical learnings from CodeSwarm development:

*   **ADK Version and Model Compatibility:**
    *   `google-adk==1.1.1` was used. `gemini-1.5-flash-latest` (or more recent flash/pro models) proved compatible.
*   **`LlmAgent` Configuration (ADK 1.1.1):**
    *   `LlmAgent` instances for Admin, Dev, and Revisor are configured with the `output_model` parameter, assigning Pydantic models (`AdminTaskOutput`, `DevAgentOutput`, `RevisorAgentOutput`) to structure their responses. This is the primary method used for ensuring reliable output parsing.
    *   The `generation_config` does not set `response_mime_type: "application/json"` when `output_model` is used, as `output_model` handles the parsing. The note about `response_mime_type` conflicting with tool usage remains relevant if tools were enabled *without* `output_model` and JSON output was still desired.
*   **Tool Usage and Dispatch:**
    *   **Granular Tasks:** AdminAgent should break down goals into small, specific tasks for reliability.
    *   **ADK-Native Tool Calls:** All agents (Admin for logging, Dev for coding, Revisor for reading) are designed to use ADK's native tool calling mechanism, facilitated by their assigned `tools` (e.g., `admin_tools_adk`, `dev_tools_adk`) and `output_model`.
    *   **Cognitive Tasks:** Use `tools_override=[]` for agents or specific agent phases not needing tools (e.g., the initial task generation phase of AdminAgent).
*   **Path Handling:**
    *   AdminAgent is prompted to generate absolute paths in its task definitions, based on the `target_project_path`.
    *   The orchestrator validates these paths against the `target_project_path` for safety before passing them to DevAgents.
*   **Session Management (ADK 1.1.1):**
    *   `InMemorySessionService` is used. Ensure the same service instance is used for session creation and `Runner`.
    *   Consistent `user_id` is crucial when creating and retrieving sessions.
    *   `session.state` is vital for passing contextual data (project goals, file paths) between orchestrator and agents, and for input grounding in prompts.
*   **Asynchronous Operations:** Core ADK operations (`create_session`, `runner.run_async`) are `async` and require `await`.
*   **Import Paths & Callbacks (ADK 1.1.1):**
    *   Use official ADK import paths (e.g., `google.adk.sessions.InMemorySessionService`).
    *   Callbacks are function-based (e.g., `before_model_callback`), using `CallbackContext` and `ToolContext`.
*   **Project Documentation:**
    *   Ongoing tasks and progress are tracked in `docs/tasklist.md`.
    *   Historical changes and task updates are logged by AdminAgent in `docs/changelog.log` and `docs/tasklist.md` respectively.

This document provides a blueprint for CodeSwarm. Detailed designs evolve with ongoing implementation and testing. For a detailed evolution and specific debugging notes, see `docs/codeswarm_development_evolution.md`.