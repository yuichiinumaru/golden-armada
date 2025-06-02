**Note:** This document outlines the initial refactoring plan for transitioning CodeSwarm to the Google Agent Development Kit (ADK). Many of the phased tasks described herein have been completed. For the current project architecture and detailed specifications, please refer to `docs/project.md`. For ongoing and future tasks, consult `docs/tasklist.md`. The 'Key ADK Concepts' section at the end of this document remains a valuable reference.

Okay, this is a solid plan. Let's outline the steps to refactor your CodeSwarm project to ADK, including a suggested file and folder architecture and incorporating lessons learned.

## Proposed File/Folder Architecture

```
codeswarm/
├── .env                      # API keys, model configs, default paths (existing, ensure it's in .gitignore)
├── main_adk_controller.py    # Main orchestration script using ADK
├── adk_config.py             # Centralized loading of .env variables, model names, API keys
│
├── adk_core/                 # Core ADK-specific components
│   ├── __init__.py           # Includes function-based callback definitions (log_llm_start, etc.)
│   ├── adk_setup.py          # Functions for ADK runner initialization, session service setup
│   ├── tool_definitions.py   # Defines ADK FunctionTools, wrapping functions from tool_logic.py
│   └── tool_logic.py         # Contains the actual Python functions for tools
│
├── adk_agents/               # ADK Agent definitions
│   ├── __init__.py           # Exports agent creation functions, may define Pydantic output models
│   ├── prompts_adk.py        # Contains functions returning instruction strings for ADK agents
│   ├── admin_agent.py        # Defines the Admin LlmAgent (potentially with Pydantic output_model)
│   ├── dev_agent.py          # Defines the Dev LlmAgent template
│   └── revisor_agent.py      # Defines the Revisor LlmAgent template
│
├── docs/                     # Project documentation (existing)
│   ├── changelog.log         # Main changelog updated by AdminAgent
│   ├── tasklist.md           # Main tasklist updated by AdminAgent
│   ├── plan.md               # This file
│   ├── project.md            # Main project specification
│   ├── (other existing docs like solidstatemgt.md, adk-imports.md)
├── project_logs/             # Potentially for other future detailed operational logs
│
├── generated_code/           # Default output for new projects (existing)
│
├── requirements.txt          # Project dependencies
└── README.md                 # Updated project README for ADK version
```

**Rationale for this structure:**

*   **`adk_config.py`**: Centralizes environment variable loading and model/API key access. Ensures `GOOGLE_API_KEY` is set for ADK.
*   **`adk_core/`**:
    *   `__init__.py`: Now also a place for defining shared ADK callback functions (e.g., `log_llm_start`, `log_tool_end`) that use `CallbackContext` and `ToolContext`.
    *   `adk_setup.py`: Encapsulates ADK `Runner` initialization and `SessionService` setup (e.g., `InMemorySessionService` or `FileStore`-backed).
    *   `tool_logic.py`: Contains the Python functions for tools, returning dictionaries.
    *   `tool_definitions.py`: Wraps functions from `tool_logic.py` into ADK `FunctionTool` objects.
*   **`adk_agents/`**:
    *   `__init__.py`: Can also define shared Pydantic models if agents use `output_model` for structured JSON.
    *   `prompts_adk.py`: Separates instruction strings.
    *   Individual agent files: Define `LlmAgent` instances, assign tools, instruction, model, and importantly, callback functions. If structured output is needed, assign a Pydantic class to `output_model`.
*   `main_adk_controller.py`: Primary orchestrator, handles `async` operations and session management.

## Detailed Refactoring Plan (Updated with Lessons Learned)

**Phase 0: Project Setup & Initial Configuration**

1.  **Backup Current Project.**
2.  **Verify/Create Directory Structure** as above.
3.  **Update `requirements.txt`:**
    *   `google-genai` (This is the SDK for calling the Gemini API directly. `google-generativeai` is also a related package, often for client libraries. The ADK itself manages direct LLM calls, but `google-genai` might be used for specific model feature interaction or if directly calling Gemini outside ADK managed agents.)
    *   `google-adk[extensions]` (for comprehensive ADK features)
    *   `python-dotenv`, `requests`, `beautifulsoup4`, `pydantic` (if using `output_model`).
4.  **Install/Update Dependencies:** `pip install -U -r requirements.txt` (or `codeswarm/requirements.txt` as per README).
5.  **`adk_config.py`:**
    *   Load `.env`. Define model strings.
    *   Critically, ensure `os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")` (or similar) is executed early for ADK `LlmAgent` to pick up the Gemini API key.

**Phase 1: Tool and Callback Refactoring for ADK**

1.  **`adk_core/tool_logic.py`:**
    *   Ensure functions return dictionaries (e.g., `{"status": "success", "content": data}`).
2.  **`adk_core/tool_definitions.py`:**
    *   Import `FunctionTool` from `google.adk.tools`.
    *   Wrap `tool_logic.py` functions into `FunctionTool` instances.
3.  **`adk_core/__init__.py` (Callbacks):**
    *   Define function-based callbacks:
        ```python
        from google.adk.agents.callback_context import CallbackContext, ToolCallbackContext
        # from google.adk.tools.tool_context import ToolContext # Older path, check ADK version

        def log_llm_start(context: CallbackContext): print(f"LLM Start: {context.agent_name}")
        def log_llm_end(context: CallbackContext): print(f"LLM End: {context.agent_name}")
        def log_tool_start(context: ToolCallbackContext): print(f"Tool Start: {context.tool_name}")
        def log_tool_end(context: ToolCallbackContext): print(f"Tool End: {context.tool_name}")
        ```
    *   Ensure correct context types are used (e.g., `CallbackContext`, `ToolCallbackContext`).

**Phase 2: Agent Definition with ADK (Updated)**

1.  **`adk_agents/prompts_adk.py`:**
    *   Store instruction strings for agents. Prompts should guide LLMs for JSON output if not using `output_model`.
2.  **Agent Definition Files (e.g., `adk_agents/admin_agent.py`):**
    *   Import `LlmAgent` from `google.adk.agents`.
    *   Import configs from `adk_config`.
    *   Import prompts from `prompts_adk`.
    *   Import tools from `adk_core.tool_definitions`.
    *   Import callback functions from `adk_core`.
    *   **Pydantic Models for Structured Output (Preferred over Manual JSON Parsing):**
        *   Define Pydantic models (e.g., in `adk_agents/__init__.py` or a dedicated `models.py`).
        *   Assign to `output_model` parameter of `LlmAgent`.
    *   Example `create_admin_llm_agent()`:
        ```python
        from google.adk.agents import LlmAgent
        from ..adk_config import ADMIN_MODEL_STR
        from .prompts_adk import get_admin_instruction_string
        from ..adk_core.tool_definitions import admin_tools_adk
        from ..adk_core import log_llm_start, log_llm_end, log_tool_start, log_tool_end
        # from . import AdminTaskOutput # Assuming Pydantic model

        def create_admin_llm_agent():
            return LlmAgent(
                name="AdminAgentADK",
                instruction=get_admin_instruction_string(),
                model=ADMIN_MODEL_STR,
                tools=admin_tools_adk,
                # output_model=AdminTaskOutput, # If using Pydantic for structured output
                before_model_callback=log_llm_start,
                after_model_callback=log_llm_end,
                before_tool_callback=log_tool_start,
                after_tool_callback=log_tool_end
            )
        ```
    *   **No `JsonOutputParser`:** Remove any attempts to import or use `google.adk.output_parsers.JsonOutputParser` as it does not exist.

**Phase 3: Orchestration with `main_adk_controller.py` (Updated for Async and Session Management)**

1.  **Imports:**
    *   Correct ADK imports:
        *   `from google.adk.services.session_service import SessionService`
        *   `from google.adk.services.impl.in_memory_session_service import InMemorySessionService`
        *   `from google.adk.sessions.state import SessionState` (if directly manipulating)
        *   `from google.adk.events import Event` (Note: no `EventType` enum)
    *   Standard library: `asyncio`, `argparse`, `os`, `json`.
2.  **`adk_core/adk_setup.py`:**
    *   `get_session_service()`: Returns an instance of `InMemorySessionService` (or `FileStore`-backed for persistence).
        ```python
        from google.adk.services.impl.in_memory_session_service import InMemorySessionService
        # from google.adk.services.impl.file_store import FileStore # For persistence
        # from google.adk.services.session_service import SessionService

        def get_session_service(use_file_store: bool = False, storage_path: str = ".codeswarm_sessions"):
            if use_file_store:
                # store = FileStore(root_dir=storage_path)
                # return SessionService(store=store) # Check exact constructor
                pass # Placeholder for FileStore implementation
            return InMemorySessionService()
        ```
    *   `get_runner(agent, session_service, app_name)`:
        ```python
        from google.adk.runners import Runner
        from google.adk.agents import Agent
        from google.adk.services.session_service import SessionService # Type hint

        def get_runner(agent_instance: Agent, session_service_instance: SessionService, app_name="codeswarm"):
            return Runner(
                agent=agent_instance,
                session_service=session_service_instance,
                app_name=app_name
            )
        ```
3.  **Main Orchestration Logic (`async def main_async()`):**
    *   **Session Service Instantiation:** Create a *single* instance of `SessionService` (e.g., `session_service = get_session_service()`) and pass it to all runners.
    *   **Session Creation:**
        ```python
        session_user_id = "codeswarm_user" # Consistent user_id
        session = await session_service.create_session(user_id=session_user_id)
        session_id = session.id
        print(f"Session created with ID: {session_id} for user: {session_user_id}")
        ```
    *   **Agent Initialization:** Create agent instances.
    *   **Runner Initialization:** Create runners for each agent, *passing the same `session_service` instance to all*.
    *   **Main Loop:**
        *   **Admin - Task Definition:**
            *   `admin_runner = get_runner(admin_agent, session_service)`
            *   `admin_response = await admin_runner.run_async(session_id=session_id, user_id=session_user_id, prompt=admin_prompt_data)`
            *   Access result: `admin_output = admin_response.output` (if `output_model` is used) or `admin_response.text` (then `json.loads()` if LLM produced JSON string).
            *   Store tasks in `session.state["tasks_for_round"] = parsed_tasks` (or pass directly).
        *   **Dev/Revisor Pair Operations:**
            *   Loop through tasks. For each task:
                *   `dev_runner = get_runner(dev_agent, session_service)`
                *   `dev_response = await dev_runner.run_async(session_id=session_id, user_id=session_user_id, prompt=dev_task_prompt)`
                *   `revisor_runner = get_runner(revisor_agent, session_service)`
                *   `revisor_response = await revisor_runner.run_async(session_id=session_id, user_id=session_user_id, prompt=revisor_prompt)`
            *   Use `session.state` for inter-agent data if not passing outputs directly.
        *   **Admin - Logging:**
            *   `log_update_response = await admin_runner.run_async(session_id=session_id, user_id=session_user_id, prompt=summary_for_logging)`
    *   **Module Execution:** Run using `python -m codeswarm.main_adk_controller` from the directory *above* `codeswarm/` to handle relative imports.
    *   **CLI Arguments & Defaults:** Use `argparse`. Load defaults from `.env` via `adk_config.py`.
4.  **Error Handling & Asynchronous Operations:**
    *   All ADK calls involving agent execution or session creation/modification are typically `async` and need `await`.
    *   Wrap `await` calls in `try-except` blocks.

**Phase 4: Testing (Updated)**

1.  **Tool Testing (Unit Tests):** Verify dictionary outputs.
2.  **Basic Agent Testing (ADK Runner/Simple Scripts):**
    *   Test Admin agent with `output_model` or JSON string output.
    *   Test tool usage by Dev/Revisor.
    *   Verify callback functions are triggered.
3.  **Integration Testing (`main_adk_controller.py`):**
    *   Test `async` workflow, session creation, and consistent `user_id` usage.
    *   Verify `session.state` usage if implemented.
    *   Confirm `InMemorySessionService` correctly shares state between agent calls *within the same run*.
    *   (Future) If `FileStore` is implemented for persistence:
        *   Test `--session-id` to load previous sessions.
        *   Verify session data (like history from `session.state['history']`) is saved and loaded.

**Phase 5: Documentation & Cleanup**

1.  **Update `README.md`:** Include `python -m ...` execution, `GOOGLE_API_KEY` setup.
2.  **Review all `docs/*.md`** for consistency with these learnings.
3.  **Update `.cursorrules`** with key lessons learned (see "Key ADK Concepts" below).

**Key ADK Concepts (Updated with Lessons Learned):**

*   **`LlmAgent` Configuration:** Agents are configured with `output_model` (Pydantic models like `AdminTaskOutput`, `DevAgentOutput`, `RevisorAgentOutput`) for structured responses. `generation_config` does not use `response_mime_type: "application/json"` when `output_model` is active. Function-based callbacks are used for lifecycle events.
*   **`FunctionTool`:** Used for wrapping Python callables for ADK-native tool use by agents.
*   **Session Management:**
    *   `SessionService` (e.g., `InMemorySessionService` from `google.adk.services.impl.in_memory_session_service`): A single instance should be shared by all runners involved in a session.
    *   `await session_service.create_session(user_id=...)`: Asynchronous, requires a consistent `user_id`.
    *   `session.id`: Used to refer to the session in runner calls.
    *   `session.state`: Dictionary for storing and retrieving data within a session, accessible across agent turns if the same `session_id` is used. Crucial for input grounding.
    *   **No `google.adk.memory.ChatMessageHistory`**: History management is custom, often via `session.state` or by passing relevant summaries/outputs.
    *   **(Future for CLI Persistence)** `FileStore` from `google.adk.services.impl.file_store` could be used with `SessionService` for saving/loading sessions.
*   **ADK `Runner`:** Executes agents (`runner.run_async(user_id=..., session_id=..., new_message=...)`). Requires the same `session_service` instance that created the session.
*   **Callbacks (Function-based):** Defined and assigned to `LlmAgent` (e.g., `before_model_callback`). Use `CallbackContext`, `ToolContext` from `google.adk.agents.callback_context`. `AbstractCallbackHandler` is not used.
*   **Imports:** Generally `google.adk.*`. Refer to `docs/adk-imports.md` if it exists and is maintained.
*   **API Key:** `GOOGLE_API_KEY` environment variable is used by ADK for Gemini models.
*   **Async:** Core ADK operations are `async`/`await`.
*   **Output Parsing:** Primarily handled by `LlmAgent(output_model=MyPydanticModel)`. If not using `output_model`, instruct LLM for JSON string and parse with `json.loads()`. No `JsonOutputParser` in ADK 1.1.1.
*   **`google.adk.events.Event`**: Event objects are received in `runner.run_async`; no specific `EventType` enum, type is inferred from event attributes.
*   **Python SDK for Gemini:** ADK manages LLM calls. If direct Gemini calls are needed outside ADK, `google-genai` (or `google.generativeai` for newer client libraries) is the relevant package. The project currently uses `google-generativeai` as a dependency.
*   **Installation:** Key ADK package is `google-adk[extensions]`.

This updated plan provides a more robust path forward, leveraging our collective experience with ADK's nuances.

## Post-Initial Refactoring & Evolving Plan

The initial refactoring of CodeSwarm to the Google Agent Development Kit (ADK), guided by the phases outlined above, has been largely completed and has established a solid foundation.

Since this initial plan was formulated, the project has continued to evolve. More detailed, phased planning, tracking ongoing tasks, and incorporating new strategic directions are now primarily managed in **`docs/tasklist.md`**. This task list reflects a deeper understanding of ADK capabilities and incorporates several advanced development fronts.

Key evolutions and current strategic thrusts detailed in `docs/tasklist.md` include:

*   **Advanced Research and Tooling:**
    *   In-depth analysis of external project codebases and architectural patterns, using digests stored in `/docs/gitingest/`.
    *   Targeted research into Retrieval Augmented Generation (RAG) techniques, supported by documents in `/docs/research/RAG/`.
    *   Evaluation and integration of Model Context Protocol (MCP) tools and the `fastapi_mcp` framework for enhancing agent capabilities.
*   **Knowledge Management & Prompt Engineering:**
    *   A systematic approach to auditing, refining, and integrating a local Knowledge Base (KB) from `/codeswarm/prompts/kb/` into agent prompting strategies.
    *   Ongoing refinement of agent instructions and collaborative workflows.
*   **Continuous Testing and Refinement:**
    *   Emphasis on iterative testing of agents and tools.

The "Key ADK Concepts" section in this document provided initial guidance. A more comprehensive and continuously updated set of lessons learned, ADK-specific behaviors, and debugging notes are maintained in:

*   **`docs/codeswarm_development_evolution.md`**: Chronicles the journey, challenges, and solutions encountered during ADK development.
*   **`.cursorrules`**: Contains concise, operational rules and reminders based on practical ADK experience, including mandatory startup procedures and model usage policies.

This `plan.md` remains a valuable historical document detailing the foundational shift to ADK. For the most current development roadmap, detailed tasks, and advanced strategies, please refer to **`docs/tasklist.md`**, **`docs/project.md`**, and the other supplementary documents mentioned.
