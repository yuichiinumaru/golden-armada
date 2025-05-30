# CodeSwarm: Project Specifications for ADK/A2A Implementation

## 1. Overall Project Goal
To implement a multi-agent coding system ("CodeSwarm") focusing on collaborative code generation, review, and project management. The system will feature Admin, Developer, and Revisor agents that interact to fulfill user-defined coding and project analysis goals. All operations, especially file I/O and API calls, must be real and executable.

## 2. Rationale for Pivoting to ADK/A2A
The decision to explore Google's Agent Development Kit (ADK) and Agent-to-Agent (A2A) communication frameworks stems from challenges encountered with the previous CAMEL AI-based implementation, primarily:
*   **Error Transparency:** Difficulty in diagnosing the root cause of `NoneType` errors when interacting with the Gemini API via CAMEL, suspected to be due to unhandled API errors (e.g., token limits, rate limits, content filtering, or issues with how tool errors were propagated).
*   **Control over Interactions:** A need for more direct control over how agents interact with the LLM, manage prompts, and handle large inputs/outputs.
*   **Robustness for Advanced Features:** To better implement complex agent behaviors like sophisticated memory mechanisms, task decomposition for large data, and fine-grained error recovery.

ADK/A2A is expected to provide a more direct interface to Gemini models and clearer error reporting, facilitating a more robust and debuggable system.

## 3. Core System Components (ADK/A2A)

### 3.1. Agent Roles and Responsibilities

Agents will be implemented leveraging ADK's `LlmAgent`.

*   **AdminAgent (Project Manager):**
    *   **Responsibilities:**
        *   Understand the overall project goal and `target_project_path` from the user/orchestrator.
        *   Define and maintain project scope.
        *   **Crucially, break down complex goals into a sequence of smaller, actionable tasks.**
        *   Assign tasks to specific Dev/Revisor pairs.
        *   Output tasks in a structured JSON format. This can be achieved by using `LlmAgent(generation_config={"response_mime_type": "application/json"})` and appropriate prompting, or by using `LlmAgent(output_model=PydanticModel)`. File paths in tasks must be absolute and within the `target_project_path`.
        *   Receive summaries of Dev work and Revisor feedback.
        *   Update `codeswarm/project_logs/changelog.log` and `codeswarm/project_logs/tasklist.md` using its file I/O tools.
    *   **Tools:** File I/O (`read_file`, `write_file`, `list_folder_contents`).

*   **DevAgent (Software Developer - Template for X instances):**
    *   **Responsibilities:**
        *   Receive a specific coding/processing task.
        *   Perform operations like writing new code, modifying existing code, or generating text content.
        *   Utilize tools to read source files and write outputs to the `target_project_path`.
        *   Handle intermediate files as directed by AdminAgent.
    *   **Tools:** File I/O (`read_file`, `write_file`).

*   **RevisorAgent (Code/Content Reviewer - Template for X instances):**
    *   **Responsibilities:**
        *   Receive a file path and review instructions.
        *   Use tools to read the file and consult `codeswarm/project_logs/doclinks.md` URLs.
        *   Review for correctness, adherence to instructions, standards, etc.
        *   Generate specific, constructive feedback.
    *   **Tools:** File I/O (`read_file`), Web Browsing (`fetch_web_page_text_content`).

### 3.2. Orchestration Logic

*   A central controller script (e.g., `main_adk_controller.py`) or A2A's orchestration capabilities will manage the workflow:
    1.  User provides initial goal, `target_project_path`, number of agent pairs (X), and rounds (potentially defaulting from environment variables).
    2.  Orchestrator initializes AdminAgent, X DevAgents, X RevisorAgents.
    3.  **Round-Based Workflow:**
        *   **Admin - Task Definition:** Orchestrator provides goal, logs, `target_project_path` to Admin. Admin returns structured tasks.
        *   **Dev/Revisor Pairs (Sequential or carefully managed parallel):**
            *   **Dev Phase:** Orchestrator passes task to DevAgent_i. DevAgent_i performs task, interacts with file system via tools.
            *   **Revisor Phase:** Orchestrator passes generated file path and review instructions to RevisorAgent_i. RevisorAgent_i reviews.
        *   **Admin - Logging:** Orchestrator provides Dev outputs and Revisor feedback to Admin. Admin updates `changelog.log` and `tasklist.md`.
    4.  User feedback loop for more rounds/goals.

### 3.3. Tool Abstractions
*   Tool functions (from `adk_core/tool_logic.py`) will be wrapped by ADK `FunctionTool`.
*   **Path Safety:** All file operations must be strictly validated.
*   **Tool Error Reporting:** Tool

## 4. Key Design Considerations for ADK/A2A

### 4.1. Robust Input/Output & Memory Management
*   **Chunking & Sequential Summarization:** This is critical.
    *   DevAgents must be prepared to receive tasks to process single documents or parts of documents.
    *   AdminAgent must be responsible for the high-level strategy of breaking down large multi-document tasks.
*   **Intermediate File Storage:** DevAgents will use `write_file` to save intermediate outputs (e.g., summaries of individual documents, processed data chunks) to the `target_project_path`. The AdminAgent will then refer to these files in subsequent tasks. This forms a basic file-based "memory" or "scratchpad" for the agent team.
*   **API Key Management:**
    *   The system should support loading the `GEMINI_API_KEY` from `.env` (which ADK will use via the `GOOGLE_API_KEY` environment variable).
    *   Consider a design that could allow multiple API keys (e.g., `GEMINI_API_KEY_POOL="key1,key2,key3"` in `.env`) to be rotated or assigned to different agents/requests if necessary to distribute load, assuming ADK allows for dynamic key usage per call or per agent session.

### 4.2. Prompt Engineering
*   AdminAgent prompts must emphasize task decomposition for large inputs and structured output using Pydantic models.
*   All agent prompts should be clear, concise, and tailored to the capabilities and interaction style of ADK.
*   Agents should be instructed on how to use their tools effectively, including providing full, correct file paths.

### 4.3. Error Handling and Reporting
*   The orchestration layer must robustly catch errors from ADK agent steps or tool executions.
*   Investigate how ADK/A2A surfaces different types of errors from the Gemini API (e.g., quota exhausted, rate limit exceeded, invalid argument, content safety blocks).
*   Log these errors clearly, leveraging the function-based callback mechanism provided by ADK.
*   If an agent step fails due to a recoverable API error (e.g., transient rate limit), a retry mechanism could be considered (though this adds complexity). If it's a persistent error (e.g., prompt too large even after chunking, or consistent content filter), the task should be failed and reported.

## 5. Environment and Configuration
*   Ensure the Python environment includes the necessary libraries, specifically `google-genai` (the updated package name), `google-adk[extensions]`, `python-dotenv`, `requests`, and `beautifulsoup4`.
*   `.env` file for `GEMINI_API_KEY`, model names (e.g., `ADMIN_MODEL`, `DEV_MODEL`), `DEFAULT_PROJECT_PATH`, `DEFAULT_GOAL`, `DEFAULT_PAIRS`, and `DEFAULT_ROUNDS`.
*   The directory structure (`codeswarm/`, `codeswarm/generated_code/`, `codeswarm/project_logs/`) remains relevant.

## 6. Migration from CAMEL
*   The logical structure of agent roles (Admin, Dev, Revisor) and their high-level responsibilities can be largely ported.
*   The Python functions in `tools.py` can likely be reused with new ADK-specific `FunctionTool` wrappers.
*   The `main_controller.py` will need significant rewriting to use ADK APIs instead of CAMEL APIs, including handling asynchronous operations with `await`.

## 7. Key Learnings and ADK Specifics

Based on our implementation and debugging process, several key specifics of the current ADK Python SDK are crucial:

*   **Import Paths:** Pay close attention to official documentation and package contents (`dir(module)` can be helpful). Avoid assuming import paths based on older versions or other frameworks. For example:
    *   `Event` is imported from `google.adk.events`.
    *   `EventType` does *not* exist in `google.adk.events`.
    *   `SessionService` and `InMemorySessionService` are imported from `google.adk.sessions`.
    *   There is no `google.adk.output_parsers.JsonOutputParser`. Use Pydantic `output_model` or manual JSON parsing.
*   **Callbacks:** ADK uses a function-based callback mechanism. Define standard Python functions matching the required signature and assign them to agent parameters (e.g., `before_model_callback`, `after_tool_callback`). Do *not* attempt to import or subclass `AbstractCallbackHandler`. Use `CallbackContext` from `google.adk.agents.callback_context` and `ToolContext` from `google.adk.tools.tool_context` in callback function signatures.
*   **Session Management:** When using `InMemorySessionService`, it is critical to use the *exact same instance* of the session service when creating a session and when providing it to the `Runner`. Ensure consistency in `user_id` when creating/fetching sessions.
*   **Asynchronous Operations:** Many core ADK operations, such as creating sessions and running agents, are asynchronous (`async` functions) and must be `await`ed.
*   **Running as a Module:** To correctly handle relative imports within the `codeswarm` package, run the main script using `python -m codeswarm.main_adk_controller` from the directory *above* the `codeswarm` directory.
*   **Gemini Model SDK:** The current recommended Python package for Gemini is `google-genai`, replacing `google-generativeai`. ADK's `LlmAgent` leverages the `GOOGLE_API_KEY` environment variable for authentication. Specific model imports like `google.adk.models.gemini_models` might be necessary depending on ADK usage patterns.

This document provides a high-level blueprint and incorporates key practical learnings from working with the ADK. Detailed design of ADK agent classes, tool invocation, and A2A message formats will continue to evolve with further implementation and testing.