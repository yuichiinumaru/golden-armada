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
    - [ ] Test all tools (file I/O, web fetch, execution) within Agno agents.
- [ ] **3. Codebase Refinement:**
    - [ ] Clean up imports and structure in `codeswarm/`.
    - [ ] Review `codeswarm/agno-agents/` and integrate useful agents if needed.
    - [ ] Ensure `requirements.txt` is up-to-date in root.

### Phase 1.5: Fixes & Critical Improvements (New)
*Goal: Address immediate issues identified in `docs/report.md`.*

- [ ] **1. Agent Capabilities:**
    - [ ] Add `execute_python_code` and `execute_shell_command` to DevAgent tools in `codeswarm/agents.py`.
    - [ ] Update DevAgent prompt to encourage self-testing.
- [ ] **2. Orchestration Logic:**
    - [ ] Implement Dev-Revisor feedback loop in `agent_os.py` (allow Dev to fix rejected code in same round).
    - [ ] Implement state persistence (`codeswarm_state.json`).
- [ ] **3. Knowledge Base Integration:**
    - [ ] Load and inject KB JSONs from `codeswarm/prompts/kb/` into agent instructions.

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
