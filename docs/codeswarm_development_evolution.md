# CodeSwarm Development Evolution: Lessons and Historical Context

This document outlines the key lessons learned and evolutionary steps in the development of the CodeSwarm project. It incorporates insights from various development phases, including early work that was part of a project historically known as "Jenova Agent Nexus" (JAN). The primary focus of this document, and the project going forward, is solely on **CodeSwarm** and its development using the Google ADK (Agent Development Kit).

## 1. ADK Version Specifics and Configuration

Insights primarily from ADK version `google-adk==1.1.1` and experiences around July 2024.

*   **Model Compatibility (ADK 1.1.1):**
    *   `gemini-1.5-flash-latest` was found to be a working and compatible model.
    *   Older model versions or some specific preview versions (e.g., `gemini-pro`, `gemini-1.5-flash-preview-05-20` used in earlier phases) sometimes resulted in 404 (Not Found) errors, likely due to ADK 1.1.1 targeting an older API endpoint (e.g., `v1beta`) where these model names/versions weren't recognized or supported for `generateContent`. It's crucial to align model versions with ADK capabilities.
*   **`LlmAgent` and `output_model` (ADK 1.1.1):**
    *   Using the `output_model` parameter in `LlmAgent` to automatically parse LLM responses into Pydantic models for tool dispatch was problematic, leading to Pydantic validation errors (`Extra inputs are not permitted`).
    *   `output_model` seems more suited for parsing the LLM's response into a data Pydantic model if the LLM is instructed to output JSON matching that model's schema, rather than for direct tool dispatch. Agent responses requiring structured output (like JSON) often need manual parsing from text.
*   **`response_mime_type` Conflicts (ADK 1.1.1):**
    *   Setting `response_mime_type: "application/json"` in `generate_content_config` for an `LlmAgent` can conflict with tool usage. An agent cannot reliably have tools and be forced to output JSON via mime type with this ADK version. It's safer for agents that are guaranteed not to use tools.
*   **Internal ADK Warnings:**
    *   Warnings like `Failed to import 'google.generativeai': No module named 'google.generativeai'` might appear from ADK 1.1.1 internals, even with `google-genai` correctly installed. These may be benign if functionality is otherwise unaffected.
*   **API Key Management:**
    *   `GEMINI_API_KEY` from `.env` is primary. Ensure ADK configurations correctly map this if it expects a different name (e.g., `GOOGLE_API_KEY`).
*   **Configuration Management:**
    *   Using a `.env` file (e.g., `codeswarm/.env`) for API keys, model names, and other configurations is effective. Centralize these in a config module (e.g., `adk_config.py`).

## 2. LLM Input Grounding

*   **Direct JSON String Input is Unreliable:** Passing complex data as a single JSON string within `Part(text=...)` to an `LlmAgent` is highly unreliable for grounding. LLMs may ignore fields or misinterpret values.
*   **Solution: Use `session.state` for Grounding:**
    *   Store critical input parameters in `session.state` (e.g., `session.state['current_project_goal'] = 'The actual goal'`).
    *   Reference these directly in agent prompts using templating (e.g., `"...your task is based on {current_project_goal}..."`).
    *   This method is essential for ensuring agents use the correct, intended input values.
    *   Remember to commit state changes and re-fetch sessions if necessary.

## 3. LLM Output Formatting (Especially for JSON)

*   **Precision in Prompts is Key:** Achieving reliable, specific JSON output structures requires extremely precise, directive, and explicit prompting.
*   **Format Adherence Failures:** Models can fail to adhere to output format requests even with strong prompting.
*   **Solution: Two-Step Process for Complex JSON (AdminAgent Example):**
    *   **Interpreter Agent:** Focuses solely on understanding input and generating *content* for JSON in natural language. Ideally tool-less.
    *   **Formatter Agent:** Takes natural language output from the Interpreter and focuses solely on structuring it into the desired JSON format. Ideally tool-less.
    *   This separation of concerns improves reliability.
*   **JSON Output from Agents:** Agents providing JSON output (especially for tool calls) need to be strictly prompted to output *only* the JSON block. Prefatory text can break direct JSON parsing if not handled by specifically searching for the JSON block (e.g., using regex).

## 4. Tool Usage by LLMs

*   **Historical Context (Jenova Agent Nexus - JAN):** Early explorations with JAN laid some groundwork for understanding tool interactions, but the refined approaches below are specific to CodeSwarm's evolution.
*   **Granular Task Processing:** Migrating to an architecture where an AdminAgent generates a list of specific, action-oriented tasks (e.g., `create_or_update_file`) and the main orchestrator processes them sequentially is more reliable than expecting a single agent to handle complex, multi-step tool sequences from one prompt.
*   **Orchestrator-Managed Tool Calls:**
    *   For critical operations (file writing, script execution), having the orchestrator explicitly call tool logic based on the agent's *request* (e.g., a parsed `function_call` in its text output) is more robust than relying solely on ADK-native tool calls for every scenario. This was particularly true for the DevAgent in CodeSwarm.
    *   The orchestrator (e.g., `main_adk_controller.py`) may need to parse `function_call` JSON from the agent's text response, look up the tool, and execute it.
*   **ADK-Native Tool Calls:** For some agents (e.g., RevisorAgent, AdminLoggerAgent in certain phases), ADK's native tool dispatch mechanisms can work effectively, provided prompts and tool definitions are clear.
*   **Directive Prompts for Tool Use:**
    *   Prompts must be exceptionally clear about *which* tool to call, *when*, and *how* to derive arguments.
    *   Ground tool arguments using `session.state` (e.g., `{dev_target_file_abs_path}`).
*   **LLMs May "Fake" Success:** An LLM might output a success message *instead* of making a tool call if the prompt isn't sufficiently directive.
*   **Instructing for `function_call` JSON Output:** Prompting the LLM to produce `{"function_call": {"name": "tool_name", "args": {...}}}` makes the intent explicit.
*   **Unexpected Tool Use:** LLMs might attempt to use tools even if not explicitly instructed.
*   **Solution for Cognitive Tasks (No Tools Needed):** Provide an empty tool list (`tools_override=[]` or `tools=[]`) if an agent's role is purely cognitive.
*   **Tool Definitions (ADK):**
    *   Use `google.adk.tools.FunctionTool`.
    *   Tool logic should reside in a separate module (e.g., `tool_logic.py`).
    *   Tools should return simple dictionaries (e.g., `{'status': 'success', ...}` or `{'status': 'error', ...}`). Avoid complex error objects that might cause API issues.
*   **User Confirmation for Dangerous Tools:** Implement explicit user confirmation in the orchestrator before executing tools like `execute_python_code`.

## 5. Path Handling for Tools

*   **Admin Agents & Relative Paths:** Prompt Admin agents (especially Formatters) to output *relative* paths for files (relative to the project root).
*   **Orchestrator & Absolute Paths:** The orchestrator should combine these relative paths with the main `target_project_path` to create absolute paths.
*   **Tool Path Resolution:**
    *   Tools operating on files (e.g., `write_file`, `read_file`) should ideally work with absolute paths.
    *   If handling potentially relative paths from an LLM, resolve them against a known, secure base path (e.g., `TARGET_PROJECT_PATH_FOR_TOOLS` environment variable).
    *   Handle "rogue" absolute paths from LLMs by using only their basename against the secure base path.
    *   Be explicit about absolute vs. relative paths to avoid duplication bugs (e.g., `project_dir/project_dir/file.py`).

## 6. Prompt Engineering Iteration

*   **Iterative Process:** Expect and plan for many iterations. Test changes one at a time.
*   **Be Explicit and Redundant:** Instructions often need to be direct, explicit, and sometimes seemingly redundant. Use ALL CAPS for emphasis on critical instructions.
*   **Separate Format and Content Instructions:** Clearly distinguish between instructions for *output format* and *how to derive content*.
*   **Prompt Storage:** Store prompts in external JSON files and load them as needed.

## 7. Debugging ADK & LLM Interactions

*   **Log LLM I/O:** Print raw LLM inputs and outputs to understand what the LLM "saw" and produced.
*   **Centralized Logging Wrapper:** A wrapper function for executing agents can centralize request/response logging, parsing, and manual tool dispatch.
*   **Tool Debug Prints:** Add detailed debug prints within tool logic functions.
*   **Simplify Inputs:** When debugging, drastically simplify inputs to isolate processing issues.
*   **Isolate Agents:** Test agents in isolation, sometimes tool-less, to verify core cognitive tasks.
*   **ADK Callbacks:** ADK 1.1.1 uses function-based callbacks (e.g., `before_model_callback`) for observing agent lifecycle events.

## 8. Orchestration Flow (CodeSwarm Specific)

*   The main controller (`main_adk_controller.py`) is responsible for the overall flow: Admin interpretation -> Admin task formatting -> Dev execution -> Revisor review -> Admin logging.
*   This can be managed in a loop for multiple rounds or tasks.
*   The orchestrator plays a key role in managing `session.state` for data flow and in dispatching certain tool calls.

## 9. Session Management (ADK 1.1.1)

*   `InMemorySessionService` is suitable for transient sessions.
*   Use a consistent `user_id` for creating and running sessions.
*   `session.state` (a dictionary) is used for data sharing across agent calls within a session.

## 10. Python Module Execution and Imports

*   Run the project as a module (e.g., `python -m codeswarm.main_adk_controller`) for correct relative imports.
*   ADK imports should use `google.adk.*`.

## Conclusion: Current Focus on CodeSwarm

The CodeSwarm project has evolved through various stages, including foundational work under the name Jenova Agent Nexus. All development efforts are now consolidated under the CodeSwarm banner, focusing on building a robust multi-agent system with the Google ADK. The lessons documented here reflect this journey and aim to guide ongoing development and refinement of CodeSwarm.

---
Files to be deleted once this merge is confirmed:
- docs/jules-notes.md
- docs/lessons.md
---
