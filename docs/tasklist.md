# Task List for CodeSwarm Project (ADK/A2A Focus)

## 0. Project Pivot & Initial ADK Setup
- [x] **Decision:** Transition from CAMEL AI to Google ADK/A2A framework.
- [x] **Rationale:** Finer control, better error handling, robust advanced features.
- [x] **Update `.cursorrules` & `conversion-notes.md`**.
- [x] **Initial ADK/A2A Setup:**
    - [x] Update `requirements.txt` and install ADK.
    - [x] Create new directory structure (`adk_core`, `adk_agents`).
- [x] **Configuration Management:**
    - [x] Create `adk_config.py` for centralized loading of `.env` variables (API keys, model choices, temperatures).
    - [x] Implement API key loading in `adk_config.py` (including `GOOGLE_API_KEY` mapping).
- [x] **Tool Abstraction Layer for ADK:**
    - [x] Create `adk_core/tool_logic.py` with core Python tool functions (returning dictionaries, simplified error outputs).
    - [x] Create `adk_core/tool_definitions.py` to wrap `tool_logic.py` functions into ADK `FunctionTool` objects.
- [x] **ADK Agent Definitions:**
    - [x] Create `adk_agents/prompts_adk.py` (and `prompts/` dir for JSON prompts) for instruction strings.
    - [x] Create `AdminAgent`, `DevAgent`, `RevisorAgent` definition files/functions in `adk_agents/` using `LlmAgent`.
- [x] **ADK Setup Helpers:**
    - [x] Create `adk_core/adk_setup.py` (basic scaffold).
- [x] **Initial Orchestration Logic (Scaffold):**
    - [x] Scaffold `main_adk_controller.py` with basic agent initialization.

## Phase 1: Critical Corrections & Core ADK Alignment
- [x] **Correct ADK Import Paths (Highest Priority):**
    - [x] Systematically update all ADK imports in the codebase to use `google.adk.` prefix.
    - [x] Corrected `EventType` import from `google.adk.events` (does not exist).
    - [x] Corrected `SessionService` import to `BaseSessionService` for type hinting in `adk_core/adk_setup.py`.
    - [x] Resolved `ImportError` for `GeminiModel` from `google.adk.models` (not typically user-imported for `LlmAgent`).
- [x] **Implement Sequential Orchestration for Dev/Revisor (Manual or `SequentialAgent`):**
    - [x] `main_adk_controller.py` uses a manual loop. (Marked as complete as current flow is established).
- [x] **Implement Structured Output for Agents (Pydantic `output_model` or Manual Parsing / `generation_config`):**
    - [x] Removed all references to non-existent `google.adk.output_parsers.JsonOutputParser`.
    - [x] AdminAgent in `adk_agents/__init__.py` uses `generation_config={"response_mime_type": "application/json"}`.
    - [x] Explored Pydantic `output_model` for AdminAgent (e.g., `AdminTaskOutput`).
    - [x] DevAgent and RevisorAgent currently rely on LLM producing parsable JSON strings. Consider defining Pydantic `output_model` or using `generation_config` for them for robustness. (Verified: Agents are already using Pydantic `output_model`s - DevAgentOutput and RevisorAgentOutput respectively as of latest review).

**[Phase 1 Complete. Key ADK alignments made.]**

## Phase 2: CLI Enhancements & Basic State Management
- [x] **Implement `argparse` for CLI Arguments:**
    - [x] In `main_adk_controller.py`, `argparse` is implemented for `path`, `goal`, `pairs`, `rounds`.
    - [x] CLI arguments include `--session-id`, `--model`, `--resume` (informational), `--list-sessions` (informational), `--debug`.
    - [x] Default values for `path`, `goal`, `pairs`, `rounds` are loaded from `.env` if not provided via CLI.
- [x] **Basic Session and Memory Management with `InMemorySessionService`:**
    - [x] In `main_adk_controller.py`:\
        - [x] Initializes `google.adk.sessions.InMemorySessionService`.
        - [x] Creates a new session for each run. `session.id` is used.
        - [x] `session.state` is used for basic inter-agent communication (e.g., passing summaries).
    - [x] Resolved `AttributeError: 'coroutine' object has no attribute 'id'` by `await`ing `create_session()`.
    - [x] Resolved `ValueError: Session not found` by ensuring consistent `user_id` (`codeswarm_orchestrator`) between session creation and `runner.run_async()` calls.
- [x] **Economical Communication (Prompt Engineering):**
    - [x] Modularized prompts into `.json` files in `codeswarm/prompts/`.
    - [x] Refined Admin prompt to avoid initial parameter requests after first round.
    - [x] Refined Dev prompt for correct tool usage and file content handling.
    - [ ] Ongoing review for conciseness and clarity to manage token usage.

**[Phase 2 Complete. Core CLI, in-memory session handling, and prompt modularization are functional.]**

## Phase 3: Robustness, Observability & Security
- [x] **Implement Robust Error Handling:**
    - [x] Add try...except blocks in `adk_core/tool_logic.py` around all tool functions. Tool errors return simplified status/message.
    - [x] Resolved Gemini API `400 INVALID_ARGUMENT` when tools returned complex errors by simplifying tool error JSON.
- [x] **Implement ADK Function-Based Callbacks for Logging:**
    - [x] Defined logging callback functions (e.g., `log_llm_start`, `log_tool_end`) in `adk_core/__init__.py`.
    - [x] Assigned these functions directly to `LlmAgent` parameters (e.g., `before_model_callback`, `after_tool_callback`) in agent creation files (`adk_agents/__init__.py`).
    - [x] Removed incorrect `CodeSwarmLoggingHandler` class and `CallbackManager` usage.
- [x] **Tool Security Measures:**
    - [x] Implement user confirmation in CLI (in `main_adk_controller.py`) before `execute_python_code` and `execute_shell_command` tools execute LLM-generated content. (Initial implementation done, needs end-to-end verification).
- [x] **Flexible Configuration (Model Selection via CLI & .env):**
    - [x] CLI model override implemented in Phase 2.
    - [x] Model parameters (e.g., temperature) configurable via `.env` and loaded in `adk_config.py`, used in `generation_config` for `LlmAgent`.
    - [x] Resolved `ValueError: LlmAgent.model_kwargs must be a dictionary` by correctly passing `generation_config`.
- [x] **Logging (Admin Agent Updates):**
    - [x] Ensure `main_adk_controller.py` enables AdminAgent to update `changelog.log` and `tasklist.md` via its ADK tools. (Verification pending successful end-to-end runs). (Code review confirms implementation is in place; orchestrator calls AdminAgent in 'logging_and_updates' phase, prompt directs log updates using 'write_file' tool, and AdminAgent has this tool.)
- [x] **Console Logging:**
    - [x] `main_adk_controller.py` includes various `print()` statements for debugging and flow tracking. Function-based callbacks also print log messages.
    - [x] Resolved issue with `LlmAgent` `debug` parameter (not a valid parameter, removed).
- [x] **Dependency Management:**
    - [x] Updated `requirements.txt`: `google-generativeai` -> `google-genai`, added `google-adk[extensions]`.
- [x] **Python Module Execution:**
    - [x] Ensured project runs correctly using `python -m codeswarm.main_adk_controller` to handle relative imports.

**[Phase 3 Largely Complete. Core error handling, callback mechanism, security prompts, and model configuration are in place. Some items need end-to-end verification.]**

## 4. Testing (Post Phase 1-3 Implementation)
- [x] Test individual tool functions in `tool_logic.py`. (Code review performed. Exposed tools are clear, handle errors, and function as described. Some unexposed tools exist. The `summarize_chunks` tool logic is different from its ADK definition, but the ADK definition is appropriate for agent-based summarization.)
- [ ] Test individual ADK agents with basic prompts (local ADK runner or script).
- [x] Test full workflow in `main_adk_controller.py` (X=1, X>1 pairs) - **IN PROGRESS, critical for overall success.**
    - [x] **RESOLVED (main_adk_controller.py):** AdminAgent Task Assignment - "Sem mensagem ou resultado inválido" error due to incorrect JSON parsing of agent's `output_text`.
    - [x] **RESOLVED (main_adk_controller.py & prompts):** AdminAgent initially failed to generate tasks, requesting parameters due to prompt conditioning. Resolved by prompt adjustments.
    - [x] **ADDRESSED (prompts_adk.py & tool_logic.py):** AdminAgent Logging - `Permission denied: '/Users'` error due to incorrect log path construction. Reinforced prompt and verified tool logic.
    - [x] **RESOLVED (DevAgent & prompts):** DevAgent `write_file` tool usage errors (KeyError: 'file_path', `None` content) due to prompt issues and agent not providing correct parameters. Addressed via prompt and ensuring DevAgent understands tool schema.
    - [x] **RESOLVED (ADK/Gemini):** `400 INVALID_ARGUMENT` error from Gemini when tools were enabled and returned detailed error JSON. Resolved by simplifying tool error JSON structure.
    - [ ] **MONITOR:** Intermittent `500 INTERNAL` server error from Google API during LLM calls. This is an external issue.
- [ ] Test with large documents (if chunking/summarization is implemented).
- [ ] Verify file operations are restricted to `target_project_path` / `generated_code`.
- [ ] Verify `project_logs/` updates (changelog, tasklist by AdminAgent).
- [ ] Test session state usage and data flow between agents via `session.state`.

## 5. Documentation
- [ ] Update `README.md` for ADK project setup, dependencies, and usage.
- [x] Update `.cursorrules` with lessons learned about ADK.
- [x] Update `changelog.log` and `tasklist.md` with recent fixes and current status. (This update)
- [ ] Update `plan.md` and `project.md` with recent findings. (Upcoming)

## Phase 6: Advanced ADK Enhancements (from sugestions.md)

### 6.1. High Impact / Near-Term Focus
- [ ] **Orquestração Avançada de Agentes:**
    - [ ] **`WorkflowAgent` para Orquestração Formal:** Encapsular a lógica de `main_adk_controller.py` (Admin -> Dev -> Revisor) usando um `WorkflowAgent` do ADK. (Ref: `academic-research`, `travel-concierge` samples).
    - [ ] **`LoopAgent` para Ciclos de Revisão/Refinamento:** Gerenciar o ciclo Dev -> Revisor com um `LoopAgent` até a aprovação ou máximo de iterações.
- [ ] **Inteligência Aprimorada com RAG (Retrieval Augmented Generation):**
    - [ ] **`DevAgent` com Conhecimento de Código Específico (RAG):** Implementar ferramenta RAG para `DevAgent` consultar Vector DB com código do projeto, documentação de bibliotecas, padrões de código, snippets. (Ref: `RAG` sample).
    - [ ] **`RevisorAgent` com Base de Conhecimento de Qualidade (RAG):** Ferramenta RAG para `RevisorAgent` consultar vulnerabilidades (OWASP), guias de estilo (PEP 8), checklists de revisão.
    - [ ] **`AdminAgent` com Contexto de Projeto (RAG):** Ferramenta RAG para `AdminAgent` consultar requisitos, decisões arquiteturais, discussões passadas.
- [ ] **Persistência e Gerenciamento de Sessão Aprimorados:**
    - [ ] **Implementar Persistência de Sessão com `FileStore`:** Usar `google.adk.services.impl.file_store.FileStore` com `InMemorySessionService` para salvar/carregar sessões (ex: em `./project_sessions`).

### 6.2. Medium Impact / Mid-Term Focus
- [ ] **Ferramentas (Tools) Mais Poderosas e Flexíveis:**
    - [ ] **Ferramentas de Análise Estática de Código:** `FunctionTool`s com linters (Flake8, Pylint) ou formatadores (Black, Ruff) para `DevAgent` ou `RevisorAgent`.
    - [ ] **Ferramentas de Teste Unitário (Esqueleto/Execução):** Ferramenta para `DevAgent` gerar esqueletos de testes; outra para executar testes existentes.
    - [ ] **Ferramentas com `ToolContext`:** Garantir que ferramentas que acessam `session.state` usem `tool_context: ToolContext`.
- [ ] **Melhorias na Experiência do Desenvolvedor e Robustez:**
    - [ ] **Callbacks Avançados para Logging e Monitoramento:** Usar callbacks ADK para log detalhado de prompts, respostas, uso de ferramentas, métricas de desempenho.
    - [ ] **Framework de Avaliação Dedicado:** Criar conjunto de tarefas de teste e scripts de avaliação (inspirado em `eval/` dos ADK samples).

### 6.3. Low Impact / Long-Term Focus (Future Vision)
- [ ] **Explorar OpenAPI Tools:** Se `codeswarm` interagir com serviços externos com OpenAPI specs.
- [ ] **Potencial para A2A (Agent-to-Agent) em Cenários Distribuídos:**
    - [ ] **Visão de Futuro: Agentes como Serviços Independentes:** Evoluir agentes para servidores ADK/MCP independentes comunicando-se via A2A.
    - [ ] **MCP (Model Context Protocol) para Interoperabilidade:** Usar MCP para comunicação entre agentes distribuídos.

---
**(Previous CAMEL-based tasks - review for relevance/adaptation to ADK/A2A)**
*Conceptual information remains useful. Core logic adapted.*

## Refactoring

- [ ] Refactor `main_adk_controller.py` to improve modularity and reduce its size. Consider breaking down the main loop and agent interaction logic into smaller, more manageable functions or classes.