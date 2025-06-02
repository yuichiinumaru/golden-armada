# Task List for CodeSwarm Project (ADK/A2A Focus)

## Current Development Phases

### Phase 1: Advanced Research & Foundation Building
*(Previously Phase 6)*
This phase focuses on systematically researching external systems, integrating existing and new knowledge base (KB) fragments, and refining the CodeSwarm agent prompting strategy. The goal is to enhance agent intelligence, consistency, adherence to complex instructions, and effective tool/MCP/RAG usage by leveraging modularized, structured knowledge and insights from other projects.

- [ ] **1. Analyze Code and Architectural Patterns from External Repository Digests (`/docs/gitingest/`):**
    - [ ] Systematically review each `.txt` file in the `/docs/gitingest/` directory.
    - [ ] For each digest file:
        - Identify the source repository/project.
        - Scan for and extract potentially relevant concepts, code structures, agent designs, tool implementations, MCP usage patterns, prompting techniques, and architectural insights that could be beneficial for CodeSwarm.
        - Focus on aspects compatible with or adaptable to the ADK/A2A/Gemini framework.
        - Document findings, noting specific file paths or code snippets within the digest that warrant further investigation or could inspire CodeSwarm features.
        - Consider how these findings might inform the development of new tools, agents, or prompt KBs for CodeSwarm.

- [ ] **2. Extract Insights from RAG Research Documents (`/docs/research/RAG/`):**
    - [ ] Review each document within the `/docs/research/RAG/` directory.
    - [ ] Identify key RAG techniques, architectural patterns, implementation strategies (e.g., HyDE, RAG-RAT), and use-case discussions.
    - [ ] Evaluate their applicability and potential benefits for enhancing CodeSwarm agents (DevAgent, RevisorAgent, AdminAgent, etc.) with RAG capabilities, particularly in the context of ADK.
    - [ ] Document relevant findings, noting specific techniques or ideas that could be prototyped or integrated into the tasks under "Phase 3: Advanced ADK Enhancements - Inteligência Aprimorada com RAG".

- [ ] **3. Audit and Analyze Existing Knowledge Base Files (`/codeswarm/prompts/kb/`):**
    - [ ] Systematically review each file within the `/codeswarm/prompts/kb/` directory.
    - [ ] For each KB file:
        - Identify its core purpose, themes, and type of knowledge (e.g., reasoning techniques, tool usage guidelines, persona definitions, domain-specific information, structured instructions in JSON, adversarial metaprompts).
        - Evaluate its current relevance, quality, and format (text, JSON, markdown).
        - Determine applicability (full or partial) to existing CodeSwarm agents (Admin, Dev, Revisor) and planned/future agents (e.g., PlannerAgent, ReporterAgent, specialized "Internal Monologue" or "Self-Correction" agents, agents interacting with MCPs/RAG).
        - Specifically note how KBs like `Reasoning Knowledge Base.json` or `adversarial-metaprompt.json` could be mapped to enhance specific agent capabilities or personas.

- [ ] **4. Extract, Refine, and Develop New KBs & System Instructions:**
    - [ ] For KBs identified as partially applicable, extract the valuable sections, instructions, or concepts.
    - [ ] Consolidate related fragments from different KBs if overlap exists.
    - [ ] Refine extracted content for clarity, conciseness, and optimal formatting for Gemini model understanding (e.g., structuring text as JSON where beneficial for adherence, keeping natural language for pure contextual knowledge).
    - [ ] Develop new, focused KB files from this refined content or for identified knowledge gaps (e.g., specific KBs for MCP tool usage guidelines, RAG interaction strategies, insights from GitIngest and RAG research).
    - [ ] Formulate or update core system instruction templates for each agent type, incorporating key directives derived from, or referencing, the KBs.

- [ ] **5. Establish a Taxonomy and Naming Convention for Knowledge Base Files:**
    - [ ] Define a clear taxonomy for organizing KB files within `/codeswarm/prompts/kb/` (and potentially for documenting insights from `/docs/gitingest/` and `/docs/research/RAG/` if not directly converted into KBs).
    - [ ] Categories could be based on:
        - **Target Agent Role(s) or Capability:** (e.g., `admin_planning.kb.json`, `dev_code_generation.kb.md`, `revisor_critique.kb.json`, `common_reasoning_framework.kb.json`, `mcp_tool_interaction_patterns.kb.md`)
        - **Knowledge Type/Function:** (e.g., `persona_definitions.kb.json`, `instructional_blocks.kb.json`, `contextual_background.kb.txt`, `tool_schemas_explained.kb.md`, `external_project_insights.md`)
        - **Format:** (Implicit in extension, but consider if grouping by format is useful).
    - [ ] Establish a consistent naming convention (e.g., `[scope]_[topic]_[type].kb.[json|md|txt]`).
    - [ ] Document this taxonomy and naming convention in a central project guide (e.g., `docs/prompt_engineering_guidelines.md` or similar).

- [ ] **6. Integrate KB References into Agent System Instructions (Prompts):**
    - [ ] Develop a standardized methodology for how agent system instructions should reference relevant KB files or specific sections (especially for JSON KBs with internal structures).
    - [ ] Explore techniques such as:
        - Explicit instructions in system prompts: "When [situation], refer to `/codeswarm/prompts/kb/[kb_file_name]#[section_key_or_header]` for [specific guidance/rules/context]."
        - Designing prompts that encourage the LLM to signal a need for specific knowledge, which could then be retrieved (if RAG/tool for KB access is available).
        - Strategically embedding core, universally applicable KB snippets directly into system instructions, while referencing larger/conditional KBs.
    - [ ] Document best practices for creating these KB-aware prompts, potentially leveraging an AI assistant (as per your established workflow) to ensure comprehensive and effective referencing.
    - [ ] Ensure prompts for agents using Tools, MCPs, or RAG include clear instructions from KBs on *how, when, where, and why* to use these capabilities, potentially drawing from the `/docs/gitingest/` and `/docs/research/RAG/` analyses.

- [ ] **7. Future Consideration: Dynamic KB Loading/RAG for Local KBs:**
    - [ ] Evaluate the feasibility of equipping agents with a dedicated ADK `FunctionTool` to dynamically load, search, and retrieve content from the `/codeswarm/prompts/kb/` files (and potentially summarized insights from `/docs/gitingest/` and `/docs/research/RAG/`) during runtime. This would create a powerful local RAG system for prompt augmentation, reducing static prompt length and increasing flexibility.

### Phase 2: MCP Integration, Specialized Agents & Enhanced Logging/State
*(Previously Phase 8, with elements from old Phase 2)*

- [ ] **In-Depth Analysis of External AI Agent Frameworks & Systems (Supports MCP & Agent Design):** Conduct a systematic and in-depth analysis of the following external AI agent frameworks and systems. The objectives are to extract relevant code structures, agent designs, tool definitions, MCP usage, prompting strategies, and architectural patterns, and to formulate a 'translation plan' or a set of recommendations for adapting these findings to the CodeSwarm ADK environment. This research will inform other future development tasks.
    - `stitionai/devika`
    - `x1xhlol/system-prompts-and-models-of-ai-tools`
    - `graphlit/graphlit`
    - `FoundationAgents/MetaGPT`
    - `FoundationAgents/MetaGPT-Ext`
    - `FoundationAgents/SPO`
    - `FoundationAgents/awesome-foundation-agents`
    - `FoundationAgents/OpenManus`
    - `crewAIInc/crewAI`
    - `crewAIInc/crewAI-tools`
    - `VRSEN/agency-swarm`
    - `VRSEN/agency-swarm-lab`
Refer to `docs/advanced_development_patterns.md` for initial ideas and context.
- [ ] **Evaluate & Prototype MCP Integrations:**
    - [ ] Systematically evaluate selected MCPs (listed in `docs/mcp_integration_ideas.md`) for their utility to CodeSwarm.
    - [ ] **Target Project Task Management via MCP:** Prioritize evaluation of MCPs like `mcp-taskwarrior` or similar for enabling AdminAgent (or orchestrator) to manage a persistent task list for the *target project*.
    - [ ] Prototype integration of 1-2 high-priority MCPs (e.g., for Task Management, Code Execution, Git/Repository Analysis, or Terminal Access) as ADK `McpTool`s.
    - [ ] Document findings and best practices for MCP tool integration within CodeSwarm.
- [ ] **Design & Implement Specialized Support Agents:**
    - [ ] Design and prototype a `PlannerAgent` to assist the AdminAgent in breaking down complex goals and managing task dependencies (potentially leveraging an MCP for task management).
    - [ ] Design and prototype a `ReporterAgent` to automatically generate summaries or documentation drafts based on project activities.
    - [ ] Explore enhancing the `ResearcherAgent` with more targeted search strategies or RAG capabilities.
- [ ] **Develop Granular State Management & Logging:**
    - [ ] Design and implement a more structured approach for managing detailed project state by the AdminAgent.
    - [ ] **CodeSwarm Operational Logging:** Ensure AdminAgent (or relevant components) can update `project_logs/changelog.log` for CodeSwarm's own operational logging (Verification pending successful end-to-end runs of this specific logging target).
    - [ ] Investigate and implement strategies for more detailed "internal monologue" or reasoning step logging from all agents, potentially using ADK callbacks and structured log formats.
- [ ] **Develop Dockerized Environment for CodeSwarm & MCPs:**
    - [ ] Investigate creating a `docker-compose.yml` or similar Docker configuration to deploy CodeSwarm alongside selected MCP tool dependencies.
    - [ ] Document the setup and usage of this Dockerized environment.

### Phase 3: Advanced ADK Enhancements
*(Previously Phase 7)*

#### 3.1. High Impact / Near-Term Focus (Post Phase 1 & 2 Research/Prototyping)
- [ ] **Orquestração Avançada de Agentes:**
    - [ ] **`WorkflowAgent` para Orquestração Formal:** Encapsular a lógica de `main_adk_controller.py` (Admin -> Dev -> Revisor) usando um `WorkflowAgent` do ADK. (Ref: `academic-research`, `travel-concierge` samples).
    - [ ] **`LoopAgent` para Ciclos de Revisão/Refinamento:** Gerenciar o ciclo Dev -> Revisor com um `LoopAgent` até a aprovação ou máximo de iterações.
- [ ] **Inteligência Aprimorada com RAG (Retrieval Augmented Generation):**
    - [ ] **[Note: Detailed implementation of RAG capabilities below should be informed by the findings of research tasks in Phase 1, particularly 1.1 (GitIngest Analysis) and 1.2 (RAG Document Analysis). Review these findings before deep diving into RAG tool development.]**
    - [ ] **`DevAgent` com Conhecimento de Código Específico (RAG):** Implementar ferramenta RAG para `DevAgent` consultar Vector DB com código do projeto, documentação de bibliotecas, padrões de código, snippets. (Ref: `RAG` sample).
    - [ ] **`RevisorAgent` com Base de Conhecimento de Qualidade (RAG):** Ferramenta RAG para `RevisorAgent` consultar vulnerabilidades (OWASP), guias de estilo (PEP 8), checklists de revisão.
    - [ ] **`AdminAgent` com Contexto de Projeto (RAG):** Ferramenta RAG para `AdminAgent` consultar requisitos, decisões arquiteturais, discussões passadas.
- [ ] **Persistência e Gerenciamento de Sessão Aprimorados:**
    - [ ] **Implementar Persistência de Sessão com `FileStore`:** Usar `google.adk.services.impl.file_store.FileStore` com `InMemorySessionService` para salvar/carregar sessões (ex: em `./project_sessions`).

#### 3.2. Medium Impact / Mid-Term Focus
- [ ] **Ferramentas (Tools) Mais Poderosas e Flexíveis:**
    - [ ] **Ferramentas de Análise Estática de Código:** `FunctionTool`s com linters (Flake8, Pylint) ou formatadores (Black, Ruff) para `DevAgent` ou `RevisorAgent`.
    - [ ] **Ferramentas de Teste Unitário (Esqueleto/Execução):** Ferramenta para `DevAgent` gerar esqueletos de testes; outra para executar testes existentes.
    - [ ] **Ferramentas com `ToolContext`:** Garantir que ferramentas que acessam `session.state` usem `tool_context: ToolContext`.
- [ ] **Melhorias na Experiência do Desenvolvedor e Robustez:**
    - [ ] **Callbacks Avançados para Logging e Monitoramento:** Usar callbacks ADK para log detalhado de prompts, respostas, uso de ferramentas, métricas de desempenho.
    - [ ] **Framework de Avaliação Dedicado:** Criar conjunto de tarefas de teste e scripts de avaliação (inspirado em `eval/` dos ADK samples).

#### 3.3. Low Impact / Long-Term Focus (Future Vision)
- [ ] **Explorar OpenAPI Tools:** Se `codeswarm` interagir com serviços externos com OpenAPI specs.
- [ ] **Potencial para A2A (Agent-to-Agent) em Cenários Distribuídos:**
    - [ ] **Visão de Futuro: Agentes como Serviços Independentes:** Evoluir agentes para servidores ADK/MCP independentes comunicando-se via A2A.
    - [ ] **MCP (Model Context Protocol) para Interoperabilidade:** Usar MCP para comunicação entre agentes distribuídos.

### Phase 4: Comprehensive Testing
*(Previously Phase 3)*

**Note on Testing Philosophy:** While this phase provides a dedicated period for comprehensive testing, the *development* of unit tests for individual tools and component tests for agents should ideally occur *concurrently* with their initial implementation. This promotes a "test-as-you-go" approach and helps catch issues earlier. The tasks below detail the scope of testing to be solidified and executed in this phase.

- [ ] **Individual Tool Function Unit Testing (in `adk_core/tool_logic.py`):**
    - [ ] Develop a test script (e.g., `test_tool_logic.py`) or use a testing framework (like `unittest` or `pytest`) to execute individual functions in `adk_core/tool_logic.py` with predefined inputs.
    - [ ] **Key aspects to test for each tool:**
        - Correct behavior with valid inputs (e.g., file created, content read, web page fetched).
        - Robust error handling (e.g., file not found, network error, invalid input).
        - Correctness of returned dictionary structure (status, content/message).
    - [ ] **Tools to prioritize for detailed unit testing:** (Ensure this list is comprehensive based on `tool_logic.py`)
        - `write_file`, `read_file`, `list_folder_contents`, `execute_python_code`, `execute_shell_command`, `fetch_web_page_text_content`, etc.
    - [x] *Initial code review of `tool_logic.py` performed (as per previous phase). Detailed unit tests above are still to be developed.*
- [ ] **Individual ADK Agent Component Testing:**
    - [ ] Create small test scripts that initialize individual agents (Admin, Dev, Revisor, and any new specialized agents) with mock ADK `Runner` and `SessionService` if needed, or use a lightweight local runner.
    - [ ] **Key aspects to test for each agent:** (Expand based on agent capabilities)
        - **AdminAgent:** Task generation, MCP interaction (if applicable), plan coherence.
        - **DevAgent:** Tool usage accuracy, code generation quality, RAG query formulation (if applicable).
        - **RevisorAgent:** Review accuracy, feedback constructiveness, RAG query formulation (if applicable).
    - [ ] Test agents with minimal prompts and with complex, KB-informed prompts.
    - [ ] Test agent behavior when expected tools/MCPs are/are not provided.
- [ ] **End-to-End Workflow Testing (`main_adk_controller.py` or `WorkflowAgent`):**
    - [ ] Test full workflow (X=1, X>1 pairs) - **ONGOING / IN PROGRESS, critical for overall success.**
        - *Monitor for previously resolved and new issues.*
    - [ ] **MONITOR:** Intermittent `500 INTERNAL` server error from Google API during LLM calls. (External issue, continue monitoring).
- [ ] **Large Input Handling Testing:**
    - [ ] Test handling of large inputs (e.g., large code files for RAG, extensive documentation for summarization tools) particularly if RAG/VectorDB or advanced chunking/summarization strategies are implemented.
- [ ] **Security Testing:**
    - [ ] Verify file operations are restricted to `target_project_path` / `generated_code`.
    - [ ] Verify safe execution of code/shell commands (confirm security prompts, sandboxing if any).
- [ ] **Logging & State Verification:**
    - [ ] Verify `project_logs/` updates by relevant components (e.g., operational changelog).
    - [ ] Verify AdminAgent can update the target project task list (file-based or MCP-based).
    - [ ] Test session state usage and data flow between agents via `session.state` (and `FileStore` if implemented).

### Phase 5: Code Quality & Maintainability
*(Previously Phase 4, with elements from old Phase 1)*
- [ ] **Ongoing review for conciseness and clarity in prompts to manage token usage.** (Moved from old Phase 1)
- [ ] **Refactor `main_adk_controller.py` (if not fully replaced by `WorkflowAgent`):**
    - [ ] Improve modularity and reduce its size if it remains the primary orchestrator.
    - [ ] Consider breaking down the main loop and agent interaction logic into smaller, more manageable functions or classes to enhance readability and maintainability.
- [ ] **General Codebase Review:**
    - [ ] Review for adherence to Python best practices, clarity, and robustness.
    - [ ] Ensure consistent error handling and logging patterns.

### Phase 6: Documentation (Ongoing)
*(Previously Phase 5)*
- [ ] Update `README.md` for ADK project setup, dependencies, usage, and new features (MCPs, RAG, advanced agents).
- [ ] Update `plan.md` (historical context) and `project.md` (overall architecture) with recent findings, structural changes, and new capabilities.
- [ ] Create `docs/prompt_engineering_guidelines.md` (if not already done as part of Phase 1.5).

---
## Completed Work

### Phase C0: Project Pivot & Initial ADK Setup
*(Original Phase 0)*
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

**[Original Phase 0 Complete. Foundation for ADK transition established.]**

### Phase C1: Critical Corrections & Core ADK Alignment
*(Original Phase 1)*
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    - [x] DevAgent and RevisorAgent Pydantic `output_model` usage: Verified that `DevAgentOutput` and `RevisorAgentOutput` Pydantic models are in use, enhancing robustness for JSON parsing.
=======
    - [ ] DevAgent and RevisorAgent currently rely on LLM producing parsable JSON strings. Consider defining Pydantic `output_model` or using `generation_config` for them for robustness (Mitigates known ADK 1.1.1 era challenges with reliable JSON from LLMs when tools are also involved).
>>>>>>> Stashed changes
=======
    - [ ] DevAgent and RevisorAgent currently rely on LLM producing parsable JSON strings. Consider defining Pydantic `output_model` or using `generation_config` for them for robustness (Mitigates known ADK 1.1.1 era challenges with reliable JSON from LLMs when tools are also involved).
>>>>>>> Stashed changes

**[Original Phase 1 Complete. Key ADK alignments made.]**

### Phase C2: CLI Enhancements & Basic State Management
*(Original "Current Development Phase 1")*
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

**[Original "Current Development Phase 1" Complete. Core CLI, in-memory session handling, and prompt modularization are functional.]**

### Phase C3: Robustness, Observability & Security (Core Functionality)
*(Original "Current Development Phase 2" - Completed Portions)*
- [x] **Implement Robust Error Handling:**
    - [x] Add try...except blocks in `adk_core/tool_logic.py` around all tool functions. Tool errors return simplified status/message.
    - [x] Resolved Gemini API `400 INVALID_ARGUMENT` when tools returned complex errors by simplifying tool error JSON.
- [x] **Implement ADK Function-Based Callbacks for Logging:**
    - [x] Defined logging callback functions (e.g., `log_llm_start`, `log_tool_end`) in `adk_core/__init__.py`.
    - [x] Assigned these functions directly to `LlmAgent` parameters (e.g., `before_model_callback`, `after_tool_callback`) in agent creation files (`adk_agents/__init__.py`).
    - [x] Removed incorrect `CodeSwarmLoggingHandler` class and `CallbackManager` usage.
- [x] **Tool Security Measures:**
    - [x] Implement user confirmation in CLI (in `main_adk_controller.py`) before `execute_python_code` and `execute_shell_command` tools execute LLM-generated content. (Initial implementation done, requires end-to-end verification during full testing in active Phase 4).
- [x] **Flexible Configuration (Model Selection via CLI & .env):**
    - [x] CLI model override implemented.
    - [x] Model parameters (e.g., temperature) configurable via `.env` and loaded in `adk_config.py`, used in `generation_config` for `LlmAgent`.
    - [x] Resolved `ValueError: LlmAgent.model_kwargs must be a dictionary` by correctly passing `generation_config`.
<<<<<<< Updated upstream
<<<<<<< Updated upstream
- [x] **AdminAgent Task Management & Progress Logging (CodeSwarm Project Documentation):**
    - [x] **CodeSwarm Project Documentation Logging:** Ensure `main_adk_controller.py` enables AdminAgent to update `docs/changelog.log` and `docs/tasklist.md` via its ADK tools. (Code review confirms implementation; orchestrator calls AdminAgent in 'logging_and_updates' phase, prompt directs log updates using 'write_file' tool, and AdminAgent has this tool. End-to-end verification for dynamic updates is pending full testing in active Phase 4).
=======
- [ ] **AdminAgent Task Management & Progress Logging:**
    - [ ] Enable AdminAgent (or orchestrator acting on its behalf) to update a persistent task list for the *target project* (e.g., via a dedicated file like `target_project_tasklist.md`). (Integration with MCP tools like `mcp-taskwarrior` for task management can be explored as part of Phase 7).
    - [ ] Ensure AdminAgent can update `project_logs/changelog.log` for CodeSwarm's operational logging. (Verification pending successful end-to-end runs).
>>>>>>> Stashed changes
=======
- [ ] **AdminAgent Task Management & Progress Logging:**
    - [ ] Enable AdminAgent (or orchestrator acting on its behalf) to update a persistent task list for the *target project* (e.g., via a dedicated file like `target_project_tasklist.md`). (Integration with MCP tools like `mcp-taskwarrior` for task management can be explored as part of Phase 7).
    - [ ] Ensure AdminAgent can update `project_logs/changelog.log` for CodeSwarm's operational logging. (Verification pending successful end-to-end runs).
>>>>>>> Stashed changes
- [x] **Console Logging:**
    - [x] `main_adk_controller.py` includes various `print()` statements for debugging and flow tracking. Function-based callbacks also print log messages.
    - [x] Resolved issue with `LlmAgent` `debug` parameter (not a valid parameter, removed).
- [x] **Dependency Management:**
    - [x] Updated `requirements.txt`: `google-generativeai` -> `google-genai`, added `google-adk[extensions]`.
- [x] **Python Module Execution:**
    - [x] Ensured project runs correctly using `python -m codeswarm.main_adk_controller` to handle relative imports.

<<<<<<< Updated upstream
**[Core aspects of Original "Current Development Phase 2" Complete. Outstanding items related to target project task management and CodeSwarm operational logging are integrated into active Phase 2.]**
=======
**[Phase 3 Largely Complete. Core error handling, callback mechanism, security prompts, and model configuration are in place. Some items need end-to-end verification.]**

## 4. Testing
**Note on Testing Philosophy:** While this phase provides a dedicated period for comprehensive testing, the *development* of unit tests for individual tools (from Phases 0-1) and component tests for agents (from Phase 1) should ideally occur *concurrently* with their initial implementation. This promotes a "test-as-you-go" approach and helps catch issues earlier. The tasks below detail the scope of testing to be solidified and executed in this phase.

- [ ] **Individual Tool Function Testing (in `tool_logic.py`):**
    - [ ] Develop a test script (e.g., `test_tool_logic.py`) or use a testing framework (like `unittest` or `pytest`) to execute individual functions in `adk_core/tool_logic.py` with predefined inputs.
    - [ ] **Key aspects to test for each tool:**
        - Correct behavior with valid inputs (e.g., file created, content read, web page fetched).
        - Robust error handling (e.g., file not found, network error, invalid input).
        - Correctness of returned dictionary structure (status, content/message).
    - [ ] **Tools to prioritize for testing:**
        - `write_file`: Verify file creation, content accuracy, path handling (relative/absolute robustness).
        - `read_file`: Verify content retrieval, handling of non-existent files.
        - `list_folder_contents`: Verify directory listing accuracy.
        - `execute_python_code`: Test with safe, simple scripts; verify output capture and error handling (requires careful sandboxing if run directly, or mock execution).
        - `execute_shell_command`: Similar to `execute_python_code`, test with safe commands.
        - `fetch_web_page_text_content`: Test with sample URLs, handling of network errors.
- [ ] **Individual ADK Agent Testing (Unit/Component Tests):**
    - [ ] Create small test scripts that initialize individual agents (Admin, Dev, Revisor) with mock ADK `Runner` and `SessionService` if needed, or use a lightweight local runner.
    - [ ] **Key aspects to test for each agent:**
        - **AdminAgent (Interpreter/Formatter):**
            - Input: Sample project goals, `target_project_path`.
            - Output: Verify generation of well-formed JSON task lists (for Formatter) or coherent natural language plans (for Interpreter). Test with varying complexity of goals.
        - **DevAgent:**
            - Input: Sample task descriptions (e.g., "create file X with content Y", "modify function Z in file A").
            - Output: Verify generation of correct `function_call` JSON in its text response for intended tool (e.g., `write_file` with correct parameters). Test that it can handle tasks requiring new file creation vs. modification.
        - **RevisorAgent:**
            - Input: Path to a sample code/text file, review criteria.
            - Output: Verify constructive feedback generation. Test its use of the `read_file` tool (ADK-native call).
    - [ ] Test agents with minimal prompts to check basic responsiveness and instruction following.
    - [ ] Test agent behavior when expected tools are/are not provided.
- [x] Test full workflow in `main_adk_controller.py` (X=1, X>1 pairs) - **IN PROGRESS, critical for overall success.**
    - [x] **RESOLVED (main_adk_controller.py):** AdminAgent Task Assignment - "Sem mensagem ou resultado inválido" error due to incorrect JSON parsing of agent's `output_text`.
    - [x] **RESOLVED (main_adk_controller.py & prompts):** AdminAgent initially failed to generate tasks, requesting parameters due to prompt conditioning. Resolved by prompt adjustments.
    - [x] **ADDRESSED (prompts_adk.py & tool_logic.py):** AdminAgent Logging - `Permission denied: '/Users'` error due to incorrect log path construction. Reinforced prompt and verified tool logic.
    - [x] **RESOLVED (DevAgent & prompts):** DevAgent `write_file` tool usage errors (KeyError: 'file_path', `None` content) due to prompt issues and agent not providing correct parameters. Addressed via prompt and ensuring DevAgent understands tool schema.
    - [x] **RESOLVED (ADK/Gemini):** `400 INVALID_ARGUMENT` error from Gemini when tools were enabled and returned detailed error JSON. Resolved by simplifying tool error JSON structure.
    - [ ] **MONITOR:** Intermittent `500 INTERNAL` server error from Google API during LLM calls. This is an external issue.
- [ ] Test handling of large inputs (e.g., large code files, extensive documentation) *if RAG/VectorDB or advanced chunking/summarization strategies are implemented for specific agents*. (Simple chunking for prompts has less specific test needs here beyond ensuring context limits aren't breached).
- [ ] Verify file operations are restricted to `target_project_path` / `generated_code` (Security).
- [ ] Verify `project_logs/` updates by AdminAgent (changelog) and orchestrator/AdminAgent (target project task list).
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
    - [ ] **[Note: Detailed implementation of RAG capabilities below should be informed by the findings of research tasks in Phase 8, particularly 8.1 (GitIngest Analysis) and 8.2 (RAG Document Analysis). Review these findings before deep diving into RAG tool development.]**
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

## Phase 7: Future Development - Advanced Agent Capabilities & MCP Integration
(Incorporated from tasklist_additions_temp.md)

- [ ] **In-Depth Analysis of External AI Agent Frameworks & Systems:** Conduct a systematic and in-depth analysis of the following external AI agent frameworks and systems. The objectives are to extract relevant code structures, agent designs, tool definitions, MCP usage, prompting strategies, and architectural patterns, and to formulate a 'translation plan' or a set of recommendations for adapting these findings to the CodeSwarm ADK environment. This research will inform other future development tasks.
    - `stitionai/devika`
    - `x1xhlol/system-prompts-and-models-of-ai-tools`
    - `graphlit/graphlit`
    - `FoundationAgents/MetaGPT`
    - `FoundationAgents/MetaGPT-Ext`
    - `FoundationAgents/SPO`
    - `FoundationAgents/awesome-foundation-agents`
    - `FoundationAgents/OpenManus`
    - `crewAIInc/crewAI`
    - `crewAIInc/crewAI-tools`
    - `VRSEN/agency-swarm`
    - `VRSEN/agency-swarm-lab`
Refer to `docs/advanced_development_patterns.md` for initial ideas and context.
- [ ] **Evaluate & Prototype MCP Integrations:**
    - [ ] Systematically evaluate selected MCPs (listed in `docs/mcp_integration_ideas.md`) for their utility to CodeSwarm.
    - [ ] Prototype integration of 1-2 high-priority MCPs (e.g., for Code Execution, Git/Repository Analysis, or Terminal Access) as ADK `McpTool`s.
    - [ ] Document findings and best practices for MCP tool integration within CodeSwarm.
- [ ] **Design & Implement Specialized Support Agents:**
    - [ ] Design and prototype a `PlannerAgent` to assist the AdminAgent in breaking down complex goals and managing task dependencies.
    - [ ] Design and prototype a `ReporterAgent` to automatically generate summaries or documentation drafts based on project activities.
    - [ ] Explore enhancing the `ResearcherAgent` with more targeted search strategies or RAG capabilities.
- [ ] **Develop Granular State Management & Logging:**
    - [ ] Design and implement a more structured approach for managing detailed project state by the AdminAgent.
    - [ ] Investigate and implement strategies for more detailed "internal monologue" or reasoning step logging from all agents, potentially using ADK callbacks and structured log formats.
- [ ] **Develop Dockerized Environment for CodeSwarm & MCPs:**
    - [ ] Investigate creating a `docker-compose.yml` or similar Docker configuration to deploy CodeSwarm alongside selected MCP tool dependencies.
    - [ ] Document the setup and usage of this Dockerized environment.
- [ ] **Consolidate MCP Documentation:** Merge `docs/mcp_candidates_temp.md` into `docs/mcp_integration_ideas.md` once file editing tools are stable or as a manual step. (This task refers to the merge action completed in step 2 of this plan).

## Phase 8: Advanced Research, Knowledge Base Integration, and Prompt Engineering Refinement

This phase focuses on systematically researching external systems, integrating existing and new knowledge base (KB) fragments, and refining the CodeSwarm agent prompting strategy. The goal is to enhance agent intelligence, consistency, adherence to complex instructions, and effective tool/MCP/RAG usage by leveraging modularized, structured knowledge and insights from other projects.

- [ ] **1. Analyze Code and Architectural Patterns from External Repository Digests (`/docs/gitingest/`):**
    - [ ] Systematically review each `.txt` file in the `/docs/gitingest/` directory. These files contain concatenated source code from various AI agent and MCP-related GitHub repositories.
    - [ ] For each digest file:
        - Identify the source repository/project.
        - Scan for and extract potentially relevant concepts, code structures, agent designs, tool implementations, MCP usage patterns, prompting techniques, and architectural insights that could be beneficial for CodeSwarm.
        - Focus on aspects compatible with or adaptable to the ADK/A2A/Gemini framework.
        - Document findings, noting specific file paths or code snippets within the digest that warrant further investigation or could inspire CodeSwarm features.
        - Consider how these findings might inform the development of new tools, agents, or prompt KBs for CodeSwarm.

- [ ] **2. Extract Insights from RAG Research Documents (`/docs/research/RAG/`):**
    - [ ] Review each document within the `/docs/research/RAG/` directory.
    - [ ] Identify key RAG techniques, architectural patterns, implementation strategies (e.g., HyDE, RAG-RAT), and use-case discussions.
    - [ ] Evaluate their applicability and potential benefits for enhancing CodeSwarm agents (DevAgent, RevisorAgent, AdminAgent, etc.) with RAG capabilities, particularly in the context of ADK.
    - [ ] Document relevant findings, noting specific techniques or ideas that could be prototyped or integrated into the tasks under "Phase 6: Advanced ADK Enhancements - Inteligência Aprimorada com RAG".

- [ ] **3. Audit and Analyze Existing Knowledge Base Files (`/codeswarm/prompts/kb/`):**
    - [ ] Systematically review each file within the `/codeswarm/prompts/kb/` directory.
    - [ ] For each KB file:
        - Identify its core purpose, themes, and type of knowledge (e.g., reasoning techniques, tool usage guidelines, persona definitions, domain-specific information, structured instructions in JSON, adversarial metaprompts).
        - Evaluate its current relevance, quality, and format (text, JSON, markdown).
        - Determine applicability (full or partial) to existing CodeSwarm agents (Admin, Dev, Revisor) and planned/future agents (e.g., PlannerAgent, ReporterAgent, specialized "Internal Monologue" or "Self-Correction" agents, agents interacting with MCPs/RAG).
        - Specifically note how KBs like `Reasoning Knowledge Base.json` or `adversarial-metaprompt.json` could be mapped to enhance specific agent capabilities or personas.

- [ ] **4. Extract, Refine, and Develop New KBs & System Instructions:**
    - [ ] For KBs identified as partially applicable, extract the valuable sections, instructions, or concepts.
    - [ ] Consolidate related fragments from different KBs if overlap exists.
    - [ ] Refine extracted content for clarity, conciseness, and optimal formatting for Gemini model understanding (e.g., structuring text as JSON where beneficial for adherence, keeping natural language for pure contextual knowledge).
    - [ ] Develop new, focused KB files from this refined content or for identified knowledge gaps (e.g., specific KBs for MCP tool usage guidelines, RAG interaction strategies, insights from GitIngest and RAG research).
    - [ ] Formulate or update core system instruction templates for each agent type, incorporating key directives derived from, or referencing, the KBs.

- [ ] **5. Establish a Taxonomy and Naming Convention for Knowledge Base Files:**
    - [ ] Define a clear taxonomy for organizing KB files within `/codeswarm/prompts/kb/` (and potentially for documenting insights from `/docs/gitingest/` and `/docs/research/RAG/` if not directly converted into KBs).
    - [ ] Categories could be based on:
        - **Target Agent Role(s) or Capability:** (e.g., `admin_planning.kb.json`, `dev_code_generation.kb.md`, `revisor_critique.kb.json`, `common_reasoning_framework.kb.json`, `mcp_tool_interaction_patterns.kb.md`)
        - **Knowledge Type/Function:** (e.g., `persona_definitions.kb.json`, `instructional_blocks.kb.json`, `contextual_background.kb.txt`, `tool_schemas_explained.kb.md`, `external_project_insights.md`)
        - **Format:** (Implicit in extension, but consider if grouping by format is useful).
    - [ ] Establish a consistent naming convention (e.g., `[scope]_[topic]_[type].kb.[json|md|txt]`).
    - [ ] Document this taxonomy and naming convention in a central project guide (e.g., `docs/prompt_engineering_guidelines.md` or similar).

- [ ] **6. Integrate KB References into Agent System Instructions (Prompts):**
    - [ ] Develop a standardized methodology for how agent system instructions should reference relevant KB files or specific sections (especially for JSON KBs with internal structures).
    - [ ] Explore techniques such as:
        - Explicit instructions in system prompts: "When [situation], refer to `/codeswarm/prompts/kb/[kb_file_name]#[section_key_or_header]` for [specific guidance/rules/context]."
        - Designing prompts that encourage the LLM to signal a need for specific knowledge, which could then be retrieved (if RAG/tool for KB access is available).
        - Strategically embedding core, universally applicable KB snippets directly into system instructions, while referencing larger/conditional KBs.
    - [ ] Document best practices for creating these KB-aware prompts, potentially leveraging an AI assistant (as per your established workflow) to ensure comprehensive and effective referencing.
    - [ ] Ensure prompts for agents using Tools, MCPs, or RAG include clear instructions from KBs on *how, when, where, and why* to use these capabilities, potentially drawing from the `/docs/gitingest/` and `/docs/research/RAG/` analyses.

- [ ] **7. Future Consideration: Dynamic KB Loading/RAG for Local KBs:**
<<<<<<< Updated upstream
    - [ ] Evaluate the feasibility of equipping agents with a dedicated ADK `FunctionTool` to dynamically load, search, and retrieve content from the `/codeswarm/prompts/kb/` files (and potentially summarized insights from `/docs/gitingest/` and `/docs/research/RAG/`) during runtime. This would create a powerful local RAG system for prompt augmentation, reducing static prompt length and increasing flexibility.
>>>>>>> Stashed changes
=======
    - [ ] Evaluate the feasibility of equipping agents with a dedicated ADK `FunctionTool` to dynamically load, search, and retrieve content from the `/codeswarm/prompts/kb/` files (and potentially summarized insights from `/docs/gitingest/` and `/docs/research/RAG/`) during runtime. This would create a powerful local RAG system for prompt augmentation, reducing static prompt length and increasing flexibility.
>>>>>>> Stashed changes
