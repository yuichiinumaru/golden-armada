# Revisão da Codebase Antes do Início
_Exported on 5/24/2025 at 22:14:07 GMT-3 from Cursor (0.50.7)_

---

**User**

antes de começarmos, pode dar uma lida na codebase pra ver o que entendeu a respeito dela? @codeswarm 

---

**Cursor**

Okay, I will start by exploring the codebase to understand its structure and purpose.

First, I'll list the contents of the main project directory `codeswarm/codeswarm/`.


It seems I made a mistake with the path. The user attached `codeswarm/codeswarm` and the workspace is `/f%3A/AI/codeswarm`, so the path should be `codeswarm` relative to the workspace root.

Let's try that again. I'll list the contents of the directory `codeswarm/` to understand the project structure.


Okay, I see the main files and subdirectories. Now I'll check the contents of `adk_core/` and `adk_agents/` to get a better understanding of the agent and core logic organization.


Now I'll read the main files to understand the core logic and how the agents are defined and orchestrated.

I'll start with `codeswarm/main_adk_controller.py`.


The file `main_adk_controller.py` is quite large. I'll read the remaining part.


Next, I'll examine `codeswarm/adk_config.py` to understand how configurations like API keys and model types are managed.


Now, let's look at how the agents are created. I'll read `codeswarm/adk_agents/__init__.py`, `codeswarm/adk_agents/dev_agent.py`, and `codeswarm/adk_agents/revisor_agent.py`.


Next, I'll look at the agent prompts in `codeswarm/adk_agents/prompts_adk.py`.


Now, let's look at the tool definitions and logic. I'll read `codeswarm/adk_core/tool_definitions.py` and `codeswarm/adk_core/tool_logic.py`.


Finally, I'll quickly check `codeswarm/adk_core/adk_setup.py` and `codeswarm/adk_core/__init__.py` for completeness.


Based on my review of the codebase, here's my understanding:

**Project Goal:**
The project, "CodeSwarm," aims to create a multi-agent coding system using Google's Agent Development Kit (ADK). It focuses on collaborative code generation, review, and project management, leveraging Gemini models. The core philosophy emphasizes real, executable functionalities and robust tool capabilities.

**Core Components:**
*   **`main_adk_controller.py`**: This is the central orchestrator. It handles command-line arguments (`argparse`), initializes agents, manages the main workflow (Admin -> Dev/Revisor -> Admin), and interacts with the ADK session service. It defines a round-based execution flow where the Admin agent first defines tasks, then Dev/Revisor pairs work on them, and finally, the Admin agent logs the results.
*   **`adk_config.py`**: Manages configuration, loading API keys (GEMINI_API_KEY, which is then set as GOOGLE_API_KEY for ADK) and model types (e.g., `ADMIN_MODEL_STR`) from a `.env` file. It also defines default operational parameters like project path and goal.
*   **`adk_agents/`**: This directory contains the definitions for the different types of agents:
    *   `__init__.py`: Contains a factory function `create_admin_llm_agent` to instantiate the AdminAgent.
    *   `dev_agent.py`: Contains `create_dev_llm_agent` for DevAgents.
    *   `revisor_agent.py`: Contains `create_revisor_llm_agent` for RevisorAgents.
    *   `prompts_adk.py`: Defines the detailed instruction strings (system prompts) for each agent type (Admin, Dev, Revisor), guiding their behavior and output format (e.g., AdminAgent is instructed to output JSON for task assignments).
*   **`adk_core/`**: This directory houses the core ADK-related setup and tool logic:
    *   `tool_logic.py`: Implements the actual Python functions for tools like file I/O (`read_file`, `write_file`, `list_folder_contents`, `search_files_content`), web fetching (`fetch_web_page_text_content`), and utility functions (`chunk_file`). It also includes potentially dangerous tools like `execute_python_code` and `execute_shell_command`, though these are not currently assigned to any agent in `tool_definitions.py`.
    *   `tool_definitions.py`: Wraps the functions from `tool_logic.py` into ADK `FunctionTool` objects and organizes them into lists (`admin_tools_adk`, `dev_tools_adk`, `revisor_tools_adk`) for assignment to the respective agents.
    *   `adk_setup.py`: Provides utility functions to get an ADK `Runner` instance and an `InMemorySessionService`.
    *   `__init__.py`: Defines function-based callbacks (`log_llm_start`, `log_llm_end`, `log_tool_start`, `log_tool_end`) for logging various events during an agent's lifecycle. These are passed to the `LlmAgent` instances upon creation.

**ADK Usage:**
*   **Agents:** `LlmAgent` from `google.adk.agents` is used to create role-defined agents (Admin, Dev, Revisor).
*   **Tools:** `FunctionTool` from `google.adk.tools` is used to define tools available to agents.
*   **Sessions:** `InMemorySessionService` is used for session management. The `main_adk_controller.py` creates a session and uses `session.state` for passing some data (like summaries between rounds).
*   **Orchestration:** The `main_adk_controller.py` script manually orchestrates the sequence of agent operations. It uses an `async def main_async()` function and `asyncio.run()` to manage asynchronous ADK operations.
*   **Callbacks:** Function-based callbacks are implemented in `adk_core/__init__.py` and assigned to agents for logging LLM and tool interactions. This aligns with the project's rules.
*   **Model Configuration:** Models are configured via `adk_config.py` and can be overridden via CLI arguments.
*   **Output Parsing:** The AdminAgent is instructed via its prompt to produce JSON. The `main_adk_controller.py` then parses this JSON string using `json.loads()`. The rules mention Pydantic models for `output_model` in `LlmAgent` as the preferred way for structured output, but this is not yet implemented for the AdminAgent (it uses an `output_key` and manual JSON parsing in the controller).

**Workflow:**
1.  The `main_adk_controller.py` starts, parses CLI arguments, and initializes the `InMemorySessionService` and a new session.
2.  It initializes the Admin, Dev, and Revisor agents, providing them with their respective models, tools, and callback functions.
3.  The system operates in rounds:
    *   **Admin - Task Definition:** The AdminAgent is called with the project goal, target path, round number, and previous summaries. It's expected to return a JSON string detailing tasks for Dev/Revisor pairs.
    *   **Dev Agents - Coding:** For each task, the corresponding DevAgent is invoked with the task description and file path. It uses its tools (primarily `write_file`) to produce or modify code.
    *   **Revisor Agents - Review:** For each completed Dev task, the corresponding RevisorAgent is invoked to review the specified file. It uses `read_file` and potentially `fetch_web_page_text_content`.
    *   **Admin - Logging & State Update:** The AdminAgent is called again with the outputs from Dev and Revisor agents. It's responsible for updating log files (`changelog.log`, `tasklist.md`) in a `project_logs` directory (relative to the `target_project_path`'s parent) using its file I/O tools.
4.  Session state (`session.state["summaries"]`) is updated with the round's activities and also saved to a local `codeswarm_state.json` file within the `target_project_path`.

**Key Observations:**
*   The project adheres to many of the specified rules, such as using `google.adk.*` imports, employing `LlmAgent` and `FunctionTool`, and implementing function-based callbacks.
*   There's a focus on real file operations within a `target_project_path`.
*   Error handling and logging seem to be incorporated at various levels.
*   Security considerations for dangerous tools are present in `main_adk_controller.py` with a user confirmation prompt, although these tools are not currently assigned to agents.
*   The system uses `InMemorySessionService`, meaning sessions are not persisted across runs unless manually handled by saving/loading the `codeswarm_state.json`.
*   The `SequentialAgent` mentioned in the rules for Dev/Revisor flow is commented out in `main_adk_controller.py`, and the flow is managed manually.
*   The AdminAgent's structured output (task list) is handled by instructing it to produce a JSON string and then parsing it in the controller, rather than using a Pydantic `output_model` directly in the `LlmAgent` definition as suggested as a best practice in the rules.

This provides a good overview of the CodeSwarm project's structure and functionality. Is there anything specific you'd like me to focus on next or any questions you have based on this understanding?

---

**User**

perfeito, em @docs vc encontra documentos úteis a respeito do adk e do projeto, pode dar uma lida neles e extrair o que complementaria o entendimento do projeto comparando à analise da codebase?

---

**Cursor**

Okay, I will read the specified documents in the `docs` folder and identify information that complements my understanding of the project from the codebase analysis.

First, I'll read `docs/project.md`.


Now I'll read `docs/plan.md`.


Now, I'll read `docs/tasklist.md`.


---

**User**

ok, carry on

---

**Cursor**

Now I'll read `docs/changelog.log`.


Next, I'll read `docs/adk-imports.md`.


Finally, I'll read `docs/docklinks.md`. (Assuming this is a typo and it should be `doclinks.md`)


Ah, it seems I assumed the typo. The file is indeed named `docklinks.md`. I will read that now.


Okay, I've reviewed the following documents from the `docs` folder:
*   `project.md`
*   `plan.md`
*   `tasklist.md`
*   `changelog.log`
*   `adk-imports.md`
*   `docklinks.md`

Here's what I've extracted that complements and expands upon the understanding I gained from the codebase analysis:

**1. Overarching Project Philosophy and Rationale (from `project.md`):**
*   **Explicit Pivot from CAMEL AI:** The project moved to ADK to gain better error transparency (especially with Gemini API errors like `NoneType`), more direct control over LLM interactions, and robustness for advanced features. This context was not evident from the code alone.
*   **Emphasis on Real Operations:** The "CRITICAL RULE" about no mock objects, real file operations, and real API calls is strongly emphasized in the `.cursorrules` and reiterated in `project.md`. The codebase analysis showed this is being followed.
*   **Chunking and Sequential Summarization as a Core Strategy:** `project.md` highlights the AdminAgent's crucial role in breaking down complex goals, especially those involving multiple large files, into sequential tasks. DevAgents are expected to handle these chunked tasks and use intermediate files. This strategic approach to handling large inputs is a key design principle not fully detailed in the agent prompts alone.

**2. ADK/A2A Specifics and Lessons Learned (from `project.md`, `plan.md`, `.cursorrules`):**
*   The documents (especially `project.md` and `plan.md`) serve as a "lessons learned" repository, capturing critical ADK-specific details that were likely discovered during development. This is invaluable context that the code itself doesn't explicitly state (e.g., "no `JsonOutputParser`", "function-based callbacks, not `AbstractCallbackHandler`", "importance of the same `SessionService` instance").
*   `adk-imports.md` provides a cheat sheet for ADK module imports, some of which might be for future or broader ADK capabilities not yet used in the current `codeswarm` codebase (e.g., `WorkflowAgent` types beyond `LlmAgent`, detailed `a2a.web` components). This indicates potential future directions or a general reference for ADK development.
*   **Pydantic for Structured Output:** While the codebase currently has the AdminAgent's output parsed manually in the controller, the documentation (`project.md`, `plan.md`, `.cursorrules`) strongly advocates for using Pydantic models assigned to the `output_model` parameter of `LlmAgent`. The `tasklist.md` notes that AdminAgent was updated to use a Pydantic model (`AdminTaskOutput`) but that Dev/Revisor still rely on manual parsing, indicating an area for future alignment with the documented best practice.

**3. Detailed Project Plan and Task Tracking (from `plan.md`, `tasklist.md`, `changelog.log`):**
*   `plan.md` outlines a phased approach to refactoring and development, including a proposed file architecture that the current codebase largely adheres to. This gives insight into the development methodology.
*   `tasklist.md` provides a granular view of completed and pending tasks. For example, it shows that:
    *   Core ADK alignment (imports, callbacks, output parsing) is mostly done.
    *   CLI enhancements and basic `InMemorySessionService` state management are largely complete.
    *   Robustness (error handling, security prompts) is mostly in place.
    *   Full end-to-end testing is "IN PROGRESS" and critical.
    *   AdminAgent's logging to `changelog.log` and `tasklist.md` needs verification in the full flow.
*   `changelog.log` provides a historical narrative of development, including deprecations/refactors (like the move away from `JsonOutputParser` and `AbstractCallbackHandler`) and bug fixes. This historical context explains *why* certain code structures exist.

**4. Agent Responsibilities and Workflow Nuances (from `project.md`):**
*   **AdminAgent's Logging Path:** `project.md` clarifies that the AdminAgent should write to `codeswarm/project_logs/changelog.log` and `codeswarm/project_logs/tasklist.md`, and that these paths are relative to the CodeSwarm *execution directory*, not necessarily the `target_project_path`. The current Admin prompt mentions paths like `os.path.join(target_project_path, '..', 'project_logs', '...')`. This might need careful handling to ensure paths resolve correctly based on where the script is run versus where `target_project_path` points.
*   **Intermediate File Storage:** `project.md` details the strategy of DevAgents using `write_file` to save intermediate outputs to `target_project_path`, forming a file-based "scratchpad." This reinforces the importance of the `target_project_path` as a workspace.
*   **RevisorAgent and `doclinks.md`:** The RevisorAgent's prompt in the codebase mentions `doclinks.md` with an assumed path. `project.md` also mentions `codeswarm/project_logs/doclinks.md` for the Revisor. `docklinks.md` (the actual file name) in the `docs` folder seems to be the central list of ADK/A2A documentation URLs, which might be different from the per-project `doclinks.md` intended for the Revisor to use for specific project guidelines. This distinction might be important.

**5. Environment and Execution (from `project.md`, `plan.md`, `.cursorrules`):**
*   The strong emphasis on running scripts as modules (e.g., `python -m codeswarm.main_adk_controller`) to ensure correct relative imports is a critical operational detail highlighted in the docs and `.cursorrules`.
*   The `requirements.txt` details (`google-genai`, `google-adk[extensions]`) are consistently mentioned.

**Areas where documentation provides significant complementary understanding:**

*   **Evolution and Rationale:** The *why* behind architectural choices (e.g., pivot to ADK, callback style) is much clearer from the documents.
*   **Detailed ADK Best Practices and Pitfalls:** The "lessons learned" sections are invaluable for understanding how to work with ADK effectively, beyond what's explicitly in the current code.
*   **Strategic Intent:** The high-level strategies, like chunking for large files managed by the AdminAgent, are more explicitly defined in the documents.
*   **Future Work/Refinements:** The `tasklist.md` and `plan.md` point to areas that might still need work or verification (e.g., Pydantic models for Dev/Revisor, Admin logging verification, full testing).
*   **Specific Paths and Conventions:** Clarifications on log file paths for the AdminAgent.

In essence, the codebase shows *what* is implemented, while the `docs` provide the *why*, *how it evolved*, and *best practices learned along the way*, along with the *plan moving forward*. The combination gives a much richer understanding of the CodeSwarm project.

---

**User**

excelente, vamos entao começar. fui rodar agora e veja só

@Google-ADK 

---

**Cursor**

I see the problem in your terminal output. The error `AttributeError: 'str' object has no attribute 'parts'` is happening in the `log_llm_start` callback function. This occurs because the code assumes that `llm_request.config.system_instruction` is always an object with a `parts` attribute, but it seems it can sometimes be a plain string. This typically happens when the `instruction` you set for an `LlmAgent` (which is a string) is passed as the `system_instruction`.

I'll fix this by updating the `log_llm_start` function in `codeswarm/adk_core/__init__.py` to correctly handle cases where `system_instruction` might be a string or an object with `parts`.

Additionally, I noticed a debug message: `FAILED to retrieve session manually before run_async using user_id='codeswarm_orchestrator': InMemorySessionService.get_session() missing 1 required keyword-only argument: 'app_name'`. This is a non-critical issue in a debug print statement in `main_adk_controller.py`. I'll correct that as well.

Here are the changes:

First, to fix the main error in `codeswarm/adk_core/__init__.py`:


```python:codeswarm/adk_core/__init__.py
// ... existing code ...
def log_llm_start(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Logs information before an LLM call."""
    prompt_text = ""
    if llm_request.contents:
        # Attempt to get text from the last part of the last content item
        last_content = llm_request.contents[-1]
        if last_content.parts:
            # Iterate through parts to find text, as parts can be multimodal
            for part in last_content.parts:
                if hasattr(part, 'text') and part.text:
                    prompt_text = part.text
                    break
    elif llm_request.config and llm_request.config.system_instruction:
        # Fallback to system instruction if contents are empty
        system_instruction = llm_request.config.system_instruction
        if hasattr(system_instruction, 'parts') and system_instruction.parts:
            prompt_text = system_instruction.parts[0].text or ""
        elif isinstance(system_instruction, str):
            prompt_text = system_instruction
        # If system_instruction is neither a string nor has parts, prompt_text remains ""

    print(f"[LLM Start] Agent: {callback_context.agent_name}, Prompt: {prompt_text[:120]}...")
    return None # Allow ADK to proceed

def log_llm_end(
// ... existing code ...
```
I've modified `log_llm_start` to check if `system_instruction` is a string or an object with `parts` before trying to access `parts[0].text`.

Next, I'll fix the `get_session` call in the debug print statement in `codeswarm/main_adk_controller.py`.


```python
// ... existing code ...
def log_llm_start(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Logs information before an LLM call."""
    prompt_text = ""
    if llm_request.contents:
        # Attempt to get text from the last part of the last content item
        last_content = llm_request.contents[-1]
        if last_content.parts:
            # Iterate through parts to find text, as parts can be multimodal
            for part in last_content.parts:
                if hasattr(part, 'text') and part.text:
                    prompt_text = part.text
                    break
    elif llm_request.config and llm_request.config.system_instruction:
        # Fallback to system instruction if contents are empty
        system_instruction = llm_request.config.system_instruction
        if hasattr(system_instruction, 'parts') and system_instruction.parts:
            prompt_text = system_instruction.parts[0].text or ""
        elif isinstance(system_instruction, str):
            prompt_text = system_instruction
        # If system_instruction is neither a string nor has parts, prompt_text remains ""

    print(f"[LLM Start] Agent: {callback_context.agent_name}, Prompt: {prompt_text[:120]}...")
    return None # Allow ADK to proceed

def log_llm_end(
// ... existing code ...
```

I'll need to see the rest of the file to make the change.


```python:codeswarm/main_adk_controller.py
// ... existing code ...
        try:
            # Use MAIN_USER_ID for run_async
            print(f"DEBUG: Attempting run_async with session_id={session.id}, user_id={MAIN_USER_ID}")
            # You can also try to explicitly get the session here to see if it's found by the service
            try:
                retrieved_session_before_run = await session_service.get_session(
                    session_id=session.id, 
                    user_id=MAIN_USER_ID,
                    app_name="codeswarm"  # Added app_name
                ) 
                print(f"DEBUG: Successfully retrieved session {retrieved_session_before_run.id} manually before run_async using user_id='{MAIN_USER_ID}'.")
            except Exception as e_get:
                print(f"DEBUG: FAILED to retrieve session manually before run_async using user_id='{MAIN_USER_ID}': {e_get}")

            async for event in current_runner.run_async(
                user_id=MAIN_USER_ID,  # Corrected: Use the main session user_id
// ... existing code ...
```
I've added `app_name="codeswarm"` to the `session_service.get_session` call in the `try...except` block within `execute_agent_and_get_result`.

These changes should resolve the `AttributeError` and the incorrect debug message. Please try running your script again.

```python
// ... existing code ...
        try:
            # Use MAIN_USER_ID for run_async
            print(f"DEBUG: Attempting run_async with session_id={session.id}, user_id={MAIN_USER_ID}")
            # You can also try to explicitly get the session here to see if it's found by the service
            try:
                retrieved_session_before_run = await session_service.get_session(
                    session_id=session.id, 
                    user_id=MAIN_USER_ID,
                    app_name="codeswarm"  # Added app_name
                ) 
                print(f"DEBUG: Successfully retrieved session {retrieved_session_before_run.id} manually before run_async using user_id='{MAIN_USER_ID}'.")
            except Exception as e_get:
                print(f"DEBUG: FAILED to retrieve session manually before run_async using user_id='{MAIN_USER_ID}': {e_get}")

            async for event in current_runner.run_async(
                user_id=MAIN_USER_ID,  # Corrected: Use the main session user_id
// ... existing code ...
```

```python
// ... existing code ...
        try:
            # Use MAIN_USER_ID for run_async
            print(f"DEBUG: Attempting run_async with session_id={session.id}, user_id={MAIN_USER_ID}")
            # You can also try to explicitly get the session here to see if it's found by the service
            try:
                retrieved_session_before_run = await session_service.get_session(
                    session_id=session.id, 
                    user_id=MAIN_USER_ID,
                    app_name="codeswarm"  # Added app_name
                ) 
                print(f"DEBUG: Successfully retrieved session {retrieved_session_before_run.id} manually before run_async using user_id='{MAIN_USER_ID}'.")
            except Exception as e_get:
                print(f"DEBUG: FAILED to retrieve session manually before run_async using user_id='{MAIN_USER_ID}': {e_get}")

            async for event in current_runner.run_async(
                user_id=MAIN_USER_ID,  # Corrected: Use the main session user_id
// ... existing code ...
```

---

**User**

show, rodou aqui, mas parece que ta rolando alguns erros especificos com relação ao google ai, pode listar todos os erros dai e  3 erros:
1 - "Default value is not supported in function declaration schema for Google AI."
2 - "AttributeError: 'Event' object has no attribute 'type'"
3 - Ausência de “callbacks”


pelo que eu entendi lendo aqui a documentação, a forma de declarar as funções para que o ADK gere o esquema de chamada (FunctionDeclaration) é definir funções Python com
1 - Assinatura limpa, sem valores padrão nos parâmetros, para que todos sejam obrigatórios.
2 - Parâmetros JSON-serializáveis (por exemplo, str, int, bool, list, dict).
3 - Docstring completa, que o ADK usa como descrição da ferramenta.
4 - Retorno preferencial em forma de dicionário Python (dict), para estruturar o resultado em pares chave-valor.

dê uma checada na documentação para esses 3 aspectos. foque somente na analise por enquanto e na elucidação da resposta, nao escreva codigo ainda. @Google-ADK @Google-ADK API Reference @Google Gemini GenAI SDK Python 

---

**Cursor**

Let's analyze each of the three error types you encountered, referencing the ADK documentation and your codebase, and clarify the root causes and best practices for each:

---

### 1. "Default value is not supported in function declaration schema for Google AI."

**What it means:**
- This error is emitted by the ADK when it tries to generate a FunctionDeclaration (the schema that describes a tool/function for the LLM to call) and finds a parameter with a default value in the Python function signature.
- The Google AI Function Calling system (used by Gemini and ADK) currently only supports functions where all parameters are required—no default values allowed.

**Documentation Evidence:**
- The ADK docs and API reference (see your provided snippets and the official [FunctionTool docs](https://google.github.io/adk-docs/tools/function-tools/)) state:
  - "FunctionTool expects a Python function with a clean signature: all parameters must be required (no default values)."
  - "Default values are not supported in function declaration schema for Google AI."

**Best Practice:**
- All tool functions (those decorated with `@FunctionTool`) must have signatures where every parameter is required and has no default value.
- Example (correct):
  ```python
  @FunctionTool
  def write_file(file_path: str, content: str) -> dict:
      """Writes content to a file."""
      ...
  ```
- Example (incorrect):
  ```python
  @FunctionTool
  def chunk_file(file_path: str, max_chunk_size: int = 4000) -> dict:  # Not allowed!
      ...
  ```
  - Here, `max_chunk_size` has a default value, which will trigger the error.

---

### 2. "AttributeError: 'Event' object has no attribute 'type'"

**What it means:**
- Your code is trying to access the `.type` attribute on an `Event` object returned by ADK, but the current ADK version's `Event` class does not have a `.type` attribute.
- This is likely due to changes in the ADK API, where event types are now inferred from other attributes or the class itself, not a `.type` field.

**Documentation Evidence:**
- The [ADK API reference for Event](https://google.github.io/adk-docs/api-reference/python/google-adk.html) and your own `adk-imports.md` note:
  - There is no `EventType` enum or `.type` attribute on the `Event` class.
  - Event type is typically inferred from the class (`isinstance(event, UserEvent)`, etc.) or from other fields like `event.data`.

**Best Practice:**
- Do not access `.type` on ADK `Event` objects.
- If you need to distinguish event types, use `isinstance(event, SomeEventClass)` or inspect other available attributes (like `event.data`, `event.actions`, etc.).
- Update all code that references `event.type` to use the correct approach.

---

### 3. Ausência de “callbacks” (callbacks not found in ADK)

**What it means:**
- The ADK does not expose a `callbacks` module or a class like `AbstractCallbackHandler` (as in LangChain or older agent frameworks).
- Instead, ADK uses function-based callbacks, which are passed directly to agent constructors (e.g., `before_model_callback`, `after_tool_callback`).

**Documentation Evidence:**
- The [ADK API reference](https://google.github.io/adk-docs/api-reference/python/google-adk.html) and your own `adk-imports.md` confirm:
  - There is no `google.adk.callbacks` module.
  - The correct way is to define Python functions (with the right signature) and assign them to the agent's callback parameters.
  - Example from docs:
    ```python
    def log_llm_start(context: CallbackContext, llm_request: LlmRequest): ...
    agent = LlmAgent(
        ...,
        before_model_callback=log_llm_start,
        ...
    )
    ```

**Best Practice:**
- Use function-based callbacks, not class-based handlers.
- Assign your logging or policy functions directly to the agent's callback parameters.
- Use the correct context types (`CallbackContext`, `ToolContext`) as function arguments.

---

## Summary Table

| Error/Aspect | Root Cause | Documentation Guidance | Best Practice |
|--------------|------------|-----------------------|--------------|
| Default value in function | FunctionTool does not support default values in parameters | All parameters must be required, no defaults | Remove all default values from tool function signatures |
| Event `.type` attribute | ADK Event objects do not have `.type` | Event type is inferred, not a field | Use `isinstance` or inspect other fields, not `.type` |
| Callbacks module/class | No `callbacks` module/class in ADK | Use function-based callbacks, assign to agent | Define and assign functions directly, use correct context types |

---

## Actionable Next Steps

- **Audit all tool functions**: Remove any default values from their signatures.
- **Update all event handling code**: Replace `.type` attribute access with `isinstance` or other supported checks.
- **Ensure all callbacks**: Are function-based, assigned directly, and use the correct context types.

If you want, I can help you identify all the places in your codebase that need to be changed for these issues. Let me know if you want a code audit or want to proceed with the fixes!

```python
  @FunctionTool
  def write_file(file_path: str, content: str) -> dict:
      """Writes content to a file."""
      ...
```

```python
  @FunctionTool
  def chunk_file(file_path: str, max_chunk_size: int = 4000) -> dict:  # Not allowed!
      ...
```

```python
    def log_llm_start(context: CallbackContext, llm_request: LlmRequest): ...
    agent = LlmAgent(
        ...,
        before_model_callback=log_llm_start,
        ...
    )
```

