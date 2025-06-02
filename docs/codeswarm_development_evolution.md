# CodeSwarm Development Evolution: Lessons and Historical Context

This document outlines the key lessons learned and evolutionary steps in the development of the CodeSwarm project. It incorporates insights from various development phases, including early work that was part of a project historically known as "Jenova Agent Nexus" (JAN). The primary focus of this document, and the project going forward, is solely on **CodeSwarm** and its development using the Google ADK (Agent Development Kit).

## 1. ADK Version Specifics and Configuration (Primarily ADK `google-adk==1.1.1`)

Experiences and lessons learned, particularly with `google-adk==1.1.1`.

*   **Model Compatibility (with ADK 1.1.1):**
    *   `gemini-2.5-flash-preview-05-20` was identified as a working and compatible model with the Google ADK 1.1.1 setup used during a significant development and stabilization phase.
    *   Initial attempts with other models (e.g., `gemini-pro` or other preview versions) sometimes resulted in `404 Not Found` errors. This was likely due to ADK 1.1.1 targeting an older API endpoint (e.g., `v1beta`) where those model names/versions weren't recognized or supported for `generateContent`.
    *   *Note:* Model compatibility is highly dependent on the ADK version and the backend API it targets. Always verify with the specific ADK version in use.

*   **Google ADK 1.1.1 Limitations & Characteristics:**
    *   **`output_model` Parameter:** The `output_model` parameter for `LlmAgent` (intended for Pydantic model integration for structured output parsing) was found to be not reliably supported as documented for later Pydantic v2 integration with ADK 1.1.1. Agent responses requiring structured output (like JSON) often needed manual parsing from the agent's text response or reliance on `generation_config` if no tools were used by the agent. Using `output_model` for tool dispatch often led to Pydantic validation errors (e.g., `Extra inputs are not permitted`).
    *   **`response_mime_type` Conflicts:** Setting `response_mime_type: "application/json"` in `LlmAgent`'s `generation_config` was found to conflict with the use of function calling (tools). An agent could not reliably have tools and be forced to output JSON via this mime type with ADK 1.1.1. This setting is safer for agents guaranteed not to use tools.
    *   **Internal ADK Warnings:** A persistent diagnostic warning, `Failed to import 'google.generativeai': No module named 'google.generativeai'`, sometimes occurred. This appeared to be an internal characteristic of ADK 1.1.1, even when `google-genai` was correctly installed and used by the application code. It did not necessarily block functionality if compatible models were used.

*   **API Key Management:**
    *   `GEMINI_API_KEY` from the `.env` file is primary. `adk_config.py` should ensure this is mapped to `GOOGLE_API_KEY` if the latter is not set, as ADK services typically expect `GOOGLE_API_KEY`.

*   **Configuration Management:**
    *   Using a `.env` file (e.g., `codeswarm/.env`) for API keys, model names, temperatures, and other configurations is an effective practice. Centralize the loading and access of these in a configuration module (e.g., `adk_config.py`).

## 2. LLM Input Grounding

*   **Direct JSON String Input is Unreliable:** Passing complex data as a single JSON string within `Part(text=...)` to an `LlmAgent` is highly unreliable for grounding. LLMs may ignore fields, misinterpret values, or fail to process the input correctly.
*   **Solution: Use `session.state` for Grounding:**
    *   Store critical input parameters and contextual data in `session.state` (e.g., `session.state['current_project_goal'] = 'The actual goal'`, `session.state['target_file_path'] = '/path/to/file'`).
    *   Reference these `session.state` keys directly in agent prompts using templating (e.g., `"...your task is based on {current_project_goal} and you should write to {target_file_path}..."`).
    *   This method is essential for ensuring agents use the correct, intended input values provided by the orchestrator.
    *   Remember to commit state changes to the session and re-fetch/pass the session object if necessary between agent calls or orchestrator steps.

## 3. LLM Output Formatting (Especially for JSON)

*   **Precision in Prompts is Key:** Achieving reliable and specific JSON output structures requires extremely precise, directive, and explicit prompting.
*   **Format Adherence Failures:** Models can fail to adhere to requested output formats even with strong prompting.
*   **Solution: Two-Step Process for Complex JSON (AdminAgent Example):**
    *   **Interpreter Agent:** Focuses solely on understanding input and generating the *content* for the JSON output but in natural language. Ideally, this agent is tool-less.
    *   **Formatter Agent:** Takes the natural language output from the Interpreter Agent and focuses solely on structuring it into the desired JSON format. Ideally, this agent is also tool-less.
    *   This separation of concerns (understanding content vs. structuring format) significantly improves the reliability of generating complex JSON.
*   **JSON Output from Agents (General):** Agents providing JSON output (especially if it's to be parsed for tool calls or structured data) need to be strictly prompted to output *only* the JSON block. Prefatory text (e.g., "Thought: ...", "Here is the JSON you requested:") can break direct JSON parsing if not handled by specifically searching for and extracting the JSON block (e.g., using regex to find ```json ... ``` or `{...}`).

## 4. Tool Usage by LLMs

*   **Historical Context (Jenova Agent Nexus - JAN):** Early explorations with a precursor project (JAN) laid some groundwork for understanding tool interactions, but the refined approaches below are specific to CodeSwarm's evolution with ADK.
*   **Granular Task Processing is Key:** Migrating to an architecture where an AdminAgent generates a list of specific, action-oriented tasks (e.g., `create_or_update_file`, `execute_python_script`) and the main orchestrator (`main_adk_controller.py`) processes them sequentially proved much more reliable than expecting a single agent (e.g., DevAgent) to handle complex, multi-step tool sequences derived from a single, high-level prompt.
*   **Orchestrator-Managed Tool Calls:** For critical operations like file writing (post-DevAgent's code generation) and script execution (especially those requiring user confirmation), having the orchestrator explicitly call the tool logic (from `tool_logic.py`) based on the agent's *request* (e.g., a parsed `function_call` structure found in the agent's text output) is more robust. This approach provides better control and error handling than relying on the agent to perfectly format and execute ADK-native tool calls for every scenario, particularly for tools not directly part of its ADK-defined toolset or when complex pre/post-processing is needed around the tool call.
*   **ADK-Native Tool Calls:** For some agents (e.g., RevisorAgent, AdminLoggerAgent in certain phases), ADK's native tool dispatch mechanisms can work effectively, provided that prompts and tool definitions are clear and the agent's task aligns well with direct tool use.
*   **Directive Prompts for Tool Use:**
    *   Prompts must be exceptionally clear about *which* tool to call, *when* it should be called, and *how* to derive the arguments for the tool.
    *   Ground tool arguments using `session.state` references within the prompt (e.g., "Use the `write_file` tool with the path specified in `{dev_target_file_abs_path}`.").
*   **LLMs May "Fake" Success or Misinterpret Tool Use:** An LLM might output a success message or a description of what it *would* do *instead* of actually making the tool call if the prompt isn't sufficiently directive or if it misunderstands the conditions for tool use.
*   **Instructing for `function_call` JSON Output:** For orchestrator-managed tool calls, prompting the LLM to produce a specific JSON structure like `{"function_call": {"name": "tool_name", "args": {"param1": "value1}}}` in its text response makes the agent's intent explicit and easier for the orchestrator to parse and act upon.
*   **Unexpected Tool Use:** LLMs might attempt to use tools even if not explicitly instructed for the current step, or might hallucinate tools.
*   **Solution for Cognitive Tasks (No Tools Needed):** Provide an empty tool list (e.g., `tools_override=[]` or `tools=[]` in `LlmAgent` constructor) if an agent's role or current task is purely cognitive and does not require external actions.
*   **Tool Definitions (ADK `FunctionTool`):**
    *   Use `google.adk.tools.FunctionTool` to define tools for agents using ADK-native dispatch.
    *   The actual Python logic for these tools should reside in a separate module (e.g., `tool_logic.py`).
    *   Tool functions should return simple dictionaries (e.g., `{'status': 'success', 'result': '...'}` or `{'status': 'error', 'message': '...'}`). Avoid returning complex Python objects or deeply nested error structures directly from tool logic, as these can cause issues (e.g., `400 INVALID_ARGUMENT`) when ADK forwards tool results to the Gemini API.
*   **User Confirmation for Dangerous Tools:** Implement an explicit user confirmation step in the orchestrator before executing potentially dangerous tools like `execute_python_code` or `execute_shell_command`, even if requested by an agent. This was successfully tested by ensuring an `input()` prompt is reached in the orchestrator.

## 5. Path Handling for Tools and File Operations

*   **Admin Agents & Relative Paths:** Prompt Admin agents (especially Formatters generating task lists) to output file paths as *relative* paths (relative to the project root defined by `target_project_path`).
*   **Orchestrator & Absolute Paths:** The orchestrator is responsible for combining these relative paths with the main `target_project_path` (from user input or `.env`) to create absolute paths before passing them to tools or other agents.
*   **Tool Path Resolution:**
    *   Tools operating on files (e.g., `write_file`, `read_file` in `tool_logic.py`) should ideally work with absolute paths provided by the orchestrator.
    *   If tools must handle potentially relative paths from an LLM (less ideal), they must resolve these paths against a known, secure base path (e.g., an environment variable like `TARGET_PROJECT_PATH_FOR_TOOLS` which should be equivalent to `target_project_path`).
    *   Implement safeguards against "rogue" absolute paths from LLMs (e.g., by using only the `os.path.basename()` of a rogue path and joining it with the secure base path).
    *   Be explicit and consistent about absolute vs. relative paths throughout the system to avoid path duplication bugs (e.g., `project_dir/project_dir/file.py`). Path handling in `tool_logic.py` was refined to address such issues.

## 6. Prompt Engineering Iteration and Best Practices

*   **Iterative Process:** Expect and plan for many iterations of prompt refinement. Test changes one at a time to observe their impact.
*   **Be Explicit, Directive, and Redundant:** Instructions often need to be very direct, explicit, and sometimes seemingly redundant to ensure the LLM understands and complies. Using ALL CAPS for emphasis on critical instructions or constraints can be effective.
*   **Separate Format and Content Instructions:** Clearly distinguish in prompts between instructions for the *desired output format* (e.g., "Your response MUST be only a JSON object.") and instructions on *how to derive the content* for that output.
*   **Prompt Storage:** Store prompts in external files (e.g., JSON or text files in a `prompts/` directory) and load them dynamically in the agent creation logic. This aids organization, versioning, and modification.
*   **Prompt Engineering for Multi-Step Tool Use:** It is very challenging to get an LLM agent to reliably perform a sequence of different tool calls (e.g., `write_file` then `execute_python_code`) from a single, complex task description. Agents tend to complete the first dominant part (like code generation) and then fail to proceed to subsequent, different tool-using steps. Breaking tasks down into smaller, single-action steps for the agent (either by a preceding AdminAgent or by the orchestrator's design) is more effective.

## 7. Debugging ADK & LLM Interactions

*   **Log LLM I/O:** Print or log the raw LLM inputs (full prompt or `LlmRequest` content) and raw outputs (`LlmResponse.text`) to understand exactly what the LLM "saw" and what it produced before any parsing.
*   **Centralized Logging Wrapper:** Consider a wrapper function for executing agents that can centralize request/response logging, parsing logic, and orchestrator-managed tool dispatch if applicable.
*   **Tool Debug Prints:** Add detailed debug print statements within tool logic functions in `tool_logic.py` to trace their execution and data handling.
*   **Simplify Inputs:** When debugging complex interactions or unexpected LLM behavior, drastically simplify the inputs (goal, target files, context) to isolate processing issues.
*   **Isolate Agents:** Test agents in isolation (e.g., with fixed inputs, sometimes tool-less by providing `tools_override=[]`) to verify their core cognitive tasks before integrating them into the full orchestrator flow.
*   **ADK Callbacks (Function-Based for ADK 1.1.1):** ADK 1.1.1 uses function-based callbacks (e.g., `before_model_callback`, `after_tool_callback`) assigned directly to `LlmAgent` parameters. These are useful for observing agent lifecycle events and logging. Ensure correct context types (`CallbackContext`, `ToolCallbackContext`) are used.
*   **Iterative Debugging (General):** The development process often requires methodical, step-by-step verification to isolate issues across different layers: environment setup, model selection and compatibility, agent prompting, orchestrator logic, and tool execution. For example, the non-interactive nature of tools like `run_in_bash_session` when they try to use `input()` required inferring prompt display via script hangs (`EOFError`), highlighting the need for careful test design in such environments.

## 8. Orchestration Flow (CodeSwarm Specific)

*   The main controller (`main_adk_controller.py`) is responsible for the overall workflow, which typically involves: AdminAgent interpretation of the goal -> AdminAgent task formatting (producing a structured list of tasks) -> Orchestrator iterating through tasks, dispatching to DevAgent -> DevAgent execution (often requesting tool calls managed by orchestrator) -> RevisorAgent review -> AdminLoggerAgent logging results.
*   This can be managed in a loop for multiple rounds of development or for processing a list of tasks.
*   The orchestrator plays a key role in managing `session.state` for data flow between agent steps and in directly dispatching certain critical tool calls based on agent requests.

## 9. Session Management (ADK 1.1.1)

*   `InMemorySessionService` is suitable for transient sessions (state lost when the application stops).
*   A consistent `user_id` (e.g., "codeswarm_orchestrator") must be used when creating a session (`await session_service.create_session(...)`) and when running agents within that session (`runner.run_async(session_id=..., user_id=...)`) to avoid "Session not found" errors.
*   `session.state` (a dictionary) is crucial for sharing data and context across different agent calls within the same session.
*   Session creation (`await session_service.create_session(...)`) is asynchronous.

## 10. Python Module Execution and ADK Imports

*   Run the project as a module (e.g., `python -m codeswarm.main_adk_controller` from the directory *above* `codeswarm/`) to ensure correct relative imports within the `codeswarm` package work. Set `PYTHONPATH` if necessary.
*   All ADK imports should use `google.adk.*`. Direct imports from `google.generativeai` should generally be avoided in agent/tool logic, as ADK provides its own wrappers, session management, and expects interaction through its interfaces.

## 11. Summary of Key CodeSwarm ADK Development Phases & Learnings

*   **Initial ADK/A2A Project Rules & Lessons (Pre-July 2024 Foundation):**
    *   Emphasis on ADK-specific imports (`google.adk.*`).
    *   `GEMINI_API_KEY` mapping to `GOOGLE_API_KEY` in `adk_config.py`.
    *   Defining tools with `google.adk.tools.FunctionTool`, with logic in `tool_logic.py` returning simple dicts and simple error structures to avoid Gemini API `400 INVALID_ARGUMENT`.
    *   Storing prompts in external JSON files.
    *   Clear prompting for JSON output format, especially if agent uses tools (due to `response_mime_type` conflict in ADK 1.1.1).
    *   Using `InMemorySessionService` with consistent `user_id`, and `session.state` for data sharing.
    *   `LlmAgent` in ADK 1.1.1 did not take a `debug` parameter; `output_model` Pydantic integration was unreliable, favoring manual parsing.
    *   Need for `try-except` in tool logic and orchestrator.
    *   Centralized config in `adk_config.py` and CLI arg parsing.
    *   Function-based callbacks, not class-based handlers.

*   **ADK Refactor Verification & Stabilization Phase (Centered around ADK 1.1.1, e.g., Post-July 2024):**
    This phase focused on verifying, stabilizing, and refining the CodeSwarm ADK system.
    *   **Key Accomplishments:**
        *   Successfully migrated to granular, action-oriented task processing managed by the orchestrator.
        *   The `main_adk_controller.py` directly managed critical tool execution (file writing, script execution with user confirmation) based on DevAgent's structured JSON requests.
        *   Identified `gemini-2.5-flash-preview-05-20` as a compatible model with the ADK 1.1.1 setup at that time.
        *   Resolved path duplication bugs in `tool_logic.py`.
        *   Established robust configuration via `.env`.
        *   Ensured `changelog.log` updates were correctly executed by the orchestrator for the AdminLoggerAgent.
    *   **Major Challenges & Learnings Reiterated/Reinforced:**
        *   Confirmed ADK 1.1.1 limitations: `output_model` issues, `response_mime_type` conflicts with tools.
        *   Difficulty in compelling DevAgent for sequential multi-tool calls from a single prompt reinforced the move to orchestrator-managed granular tasks.
        *   The necessity of methodical, iterative debugging across all system layers.

This phase resulted in a significantly more robust core execution loop in `main_adk_controller.py` and a more stable foundation for further feature development.

## Conclusion: Current Focus on CodeSwarm

The CodeSwarm project has evolved through various stages, including foundational work that shared context with a project historically known as Jenova Agent Nexus. All development efforts are now consolidated under the CodeSwarm banner, focusing on building a robust multi-agent system with the Google ADK. The lessons documented here reflect this journey and aim to guide ongoing development and refinement of CodeSwarm.

---
*This document now effectively merges the core, non-conflicting lessons from `docs/codeswarm_development_evolution.md` and `docs/lessons.md`, prioritizing `docs/lessons.md` for specifics related to the ADK 1.1.1 phase. `docs/jules-notes.md` content should also be considered merged here if it provided unique, critical lessons not otherwise captured.*

**Files to be deleted after this merge is confirmed and reviewed:**
- `docs/lessons.md`
- `docs/jules-notes.md` (if its unique, critical lessons are now covered)
---
