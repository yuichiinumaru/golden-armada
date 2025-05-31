# Lessons Learned: ADK & JAN Project Development

This document consolidates lessons learned from various stages of development involving the Google ADK, Gemini Models, and project-specific challenges.

## Lessons from CodeSwarm ADK Development (Post-July 2024)

*   **Granular Task Processing is Key:** Migrating to an architecture where the AdminAgent generates a list of specific, action-oriented tasks (e.g., `create_or_update_file`, `execute_python_script`) and the main orchestrator (`main_adk_controller.py`) processes them sequentially proved much more reliable than expecting a single agent (e.g., DevAgent) to handle complex, multi-step tool sequences from a single prompt.
*   **Orchestrator-Managed Tool Calls:** For critical operations like file writing (post-DevAgent's code generation) and script execution (with user confirmation), having the orchestrator explicitly call the tool logic based on the agent's *request* (e.g., a parsed `function_call` in its text output) is more robust than relying on the agent to perfectly format and execute ADK-native tool calls for every scenario, especially for tools not directly part of its ADK-defined toolset.
*   **User Confirmation for Dangerous Tools:** Implementing an explicit user confirmation step in the orchestrator before executing potentially dangerous tools like `execute_python_code` or `execute_shell_command` is crucial for safety and control. This was successfully tested by ensuring the `input()` prompt is reached.
*   **Model Compatibility (ADK 1.1.1):**
    *   `gemini-1.5-flash-latest` was found to be a working and compatible model with the Google ADK 1.1.1 setup used.
    *   Initial attempts with other models (like `gemini-pro` or more specific preview versions like `gemini-1.5-flash-preview-05-20`) failed with `404 Not Found` errors, likely due to the ADK 1.1.1 targeting an older API endpoint (e.g., `v1beta`) where these model names/versions weren't recognized or supported for `generateContent`.
*   **Google ADK 1.1.1 Limitations & Characteristics:**
    *   The `output_model` parameter for `LlmAgent` is not supported as documented for later Pydantic v2 integration. Agent responses requiring structured output (like JSON) need to be manually parsed from text or rely on `generation_config` if no tools are used.
    *   Using `response_mime_type: "application/json"` in `LlmAgent`'s `generation_config` conflicts with the use of function calling (tools). An agent cannot simultaneously have tools and be forced to output JSON via mime type with this ADK version.
    *   A persistent diagnostic warning `Failed to import 'google.generativeai': No module named 'google.generativeai'` occurs. This seems to be an internal characteristic of ADK 1.1.1, as `google-genai` is correctly installed and used by the application code. It did not block functionality once compatible models were used.
*   **Path Handling for File Operations:** Resolved path duplication bugs (e.g., `project_dir/project_dir/file.py`) by making path resolution in `tool_logic.py` more resilient and ensuring that paths passed to agents and then to tools are consistently relative to the project root.
*   **Changelog Updates:** Ensured `changelog.log` is correctly updated by having the orchestrator execute the `write_file` tool call requested by the AdminLoggerAgent.
*   **Configuration Management:** Using a `.env` file (e.g., `codeswarm/.env`) for API keys, model names, and temperatures is effective for managing configurations.
*   **Prompt Engineering for Multi-Step Tool Use:** It's very challenging to get an LLM agent to reliably perform a sequence of different tool calls (e.g., `write_file` then `execute_python_code`) from a single, complex task description. Agents tend to complete the first dominant part (like code generation) and then fail to proceed to subsequent, different tool-using steps. Breaking tasks down for the agent (or by the AdminAgent into an action list) is more effective.
*   **Iterative Debugging:** The development process required methodical, step-by-step verification to isolate issues across environment setup, model selection, agent prompting, orchestrator logic, and tool execution. The non-interactive nature of `run_in_bash_session` for `input()` calls required inferring prompt display via script hangs (`EOFError`), which, while effective, highlights the need for careful test design in such environments.
*   **JSON Output from Agents:** Agents providing JSON output (especially for tool calls or structured data) need to be strictly prompted to output *only* the JSON block. Prefatory text like "Thought: ..." can break direct JSON parsing if not handled by searching for the JSON block specifically (e.g., using regex to find ```json ... ```).

## Initial Rules & Lessons from CodeSwarm ADK/A2A Project (Pre-July 2024)

*   **ADK Imports:** All ADK imports must use `google.adk.*`. Direct imports from `google.generativeai` should be minimized or handled carefully, as ADK provides its own wrappers and session management.
*   **API Key Management:** `GEMINI_API_KEY` from `.env` is primary. `adk_config.py` should map this to `GOOGLE_API_KEY` if the latter is not set, as ADK services expect `GOOGLE_API_KEY`.
*   **Tool Definitions:** Tools for ADK agents must be defined using `google.adk.tools.FunctionTool`. The actual Python logic should reside in a separate `tool_logic.py` module, returning simple dictionaries (e.g., `{'status': 'success', 'content': '...'}` or `{'status': 'error', 'message': '...'}`). Complex error objects should not be returned by tools, as they can cause issues with the Gemini API (e.g., `400 INVALID_ARGUMENT`).
*   **Agent Prompts:**
    *   Store prompts in external JSON files (e.g., `prompts/admin_prompt.json`) and load them in `adk_agents/prompts_adk.py`.
    *   Prompts must be very clear about the expected output format, especially if JSON is required. If an agent is also using tools, it cannot be forced to output JSON via `response_mime_type` (ADK 1.1.1 limitation).
    *   For agents intended to call tools, their prompts must clearly state that their *entire response* should be the JSON for the function call.
*   **Session Management (ADK 1.1.1):**
    *   `InMemorySessionService` is used for transient sessions. Session creation (`await session_service.create_session(...)`) is asynchronous.
    *   A consistent `user_id` (e.g., "codeswarm_orchestrator") must be used for creating and running sessions to avoid "Session not found" errors.
    *   `session.state` (a dictionary) can be used for basic data sharing or maintaining state across agent calls within a session.
*   **Agent Invocation:**
    *   Use `runner.run_async(...)` to invoke agents. The `new_message` to the agent should be `google.genai.types.Content(parts=[Part(text=json.dumps(input_dict))])` if passing structured input.
    *   The `LlmAgent` constructor does *not* take a `debug` parameter in ADK 1.1.1.
    *   The `output_model` Pydantic integration in `LlmAgent` was not reliably working with ADK 1.1.1; manual parsing of agent's text output (if JSON is expected) is more robust.
*   **Error Handling:** Implement `try-except` blocks within tool logic and around critical agent calls in the orchestrator.
*   **Configuration:** Centralize configuration (model names, temperatures, API keys, default paths) in `adk_config.py`, loading from `.env`.
*   **CLI Arguments:** Use `argparse` for command-line arguments, with defaults potentially coming from `.env` via `adk_config.py`.
*   **Python Module Execution:** Run the project as a module (`python -m codeswarm.main_adk_controller`) to ensure relative imports within the `codeswarm` package work correctly. Set `PYTHONPATH` if necessary.
*   **Path Handling:** Be explicit about absolute vs. relative paths. Tools operating on the file system should typically expect paths relative to the project's root working directory. `TARGET_PROJECT_PATH_FOR_TOOLS` environment variable is used by tools to resolve full paths.
*   **Pydantic Models:** Useful for defining expected structures for agent inputs/outputs, but direct parsing into these models from agent responses needs careful implementation if `output_model` in `LlmAgent` is not used.
*   **Logging vs. Callbacks:** ADK 1.1.1 uses function-based callbacks (e.g., `before_model_callback`) rather than a complex `CallbackManager` or `LoggingHandler` class for observing agent lifecycle events. These callbacks can be simple print functions or more complex loggers.
*   **Orchestration Flow:** The main controller (`main_adk_controller.py`) is responsible for the overall flow: Admin interpretation -> Admin task formatting -> Dev execution -> Revisor review -> Admin logging. This can be managed in a loop for multiple rounds or tasks.
*   **Gemini Model Naming:** Be specific with model names (e.g., `gemini-1.5-flash-latest` vs. `gemini-pro`). The ADK 1.1.1 seemed to default to a `v1beta` API that had limited model availability, causing `404` errors for some valid current model names.

```
