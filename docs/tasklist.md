# Task List for CodeSwarm Project (Agno Focus)

## Current Development Phases

### Phase 1 (Agno): Agno Migration & Stabilization
*Goal: Ensure the new Agno-based implementation is fully functional, robust, and feature-equivalent (or better) than the legacy ADK version.*

- [x] **1. Core Migration:**
    - [x] Migrate `codeswarm_agno` codebase to `codeswarm`.
    - [x] Archive legacy ADK code to `archive/codeswarm_legacy`.
    - [x] Update `README.md` and documentation.
- [ ] **2. Functional Verification:**
    - [x] Verify orchestration logic (Admin -> Dev -> Revisor flow) using mocks.
    - [ ] Verify execution with live Gemini API (Requires valid API Key).
    - [x] Test all tools (file I/O, web fetch, execution) within Agno agents.
- [ ] **3. Codebase Refinement:**
    - [ ] Clean up imports and structure in `codeswarm/`.
    - [ ] Review `codeswarm/agno-agents/` and integrate useful agents if needed.
    - [ ] Ensure `requirements.txt` is up-to-date in root.

### Phase 1.5: Fixes & Critical Improvements (From Comprehensive Report)
*Goal: Address immediate issues identified in `docs/comprehensive_report.md`.*

- [x] **1. Agent Capabilities:**
    - [x] **Enable Code Execution:** Add `execute_python_code` to `DevAgent` tools in `codeswarm/agents.py` and update `dev_prompt.json`.
    - [x] **Security:** Implement path validation in `write_file` to restrict writes to `target_project_path`.
- [x] **2. Orchestration Logic:**
    - [x] **Feedback Loop:** Implement a retry mechanism in `_run_single_task` (Dev fixes rejected code immediately).
    - [x] **State Persistence:** Implement `save_state` and `load_state` in `AgentOS`.
    - [ ] **Logging:** Replace `print` with proper thread-safe `logging`.
- [x] **3. Knowledge Base Integration:**
    - [x] **Inject KB:** Load and inject relevant KB JSONs (e.g., `Reasoning Knowledge Base.json`) into agent instructions.
- [x] **4. Testing:**
    - [x] **Fix Tool Tests:** Update `tests/test_tool_logic.py` to match current codebase.

### Phase 2: Advanced Research & Foundation Building (Continuing)
*(Previously Phase 1)*
This phase focuses on systematically researching external systems and refining the agent prompting strategy.

- [ ] **1. Analyze Code and Architectural Patterns from External Repository Digests (`/docs/gitingest/`)**
- [ ] **2. Extract Insights from RAG Research Documents (`/docs/research/RAG/`)**
- [ ] **3. Audit and Analyze Existing Knowledge Base Files (`/codeswarm/prompts/kb/`)**
- [ ] **4. Extract, Refine, and Develop New KBs & System Instructions**
- [ ] **5. Establish a Taxonomy and Naming Convention for Knowledge Base Files**
- [ ] **6. Integrate KB References into Agent System Instructions**

### Phase 3: MCP Integration & Specialized Agents
*(Previously Phase 2)*

- [ ] **Evaluate & Prototype MCP Integrations**
- [ ] **Design & Implement Specialized Support Agents**
- [ ] **Develop Granular State Management & Logging**

---
## Archived Phases (Legacy ADK)

### Phase C0-C3 (ADK): Initial ADK Implementation
*These phases covered the initial move to Google ADK, now superseded by the Agno migration.*
- [x] Initial ADK Setup
- [x] Core ADK Alignment
- [x] CLI Enhancements
- [x] Robustness & Observability

### Legacy Pending Tasks
*Tasks specific to ADK that are no longer relevant or need re-evaluation for Agno.*
- [ ] Advanced ADK Enhancements (WorkflowAgent, LoopAgent in ADK) -> *Re-evaluate for Agno orchestration.*
- [ ] Individual ADK Agent Component Testing.
