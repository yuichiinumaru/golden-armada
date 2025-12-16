# Task List for CodeSwarm Project (Agno Focus)

## Current Development Phases

### Phase 1 (Agno): Agno Migration & Stabilization
- [x] **1. Core Migration:**
    - [x] Migrate `codeswarm_agno` codebase to `codeswarm`.
    - [x] Archive legacy ADK code to `archive/codeswarm_legacy`.
    - [x] Update `README.md` and documentation.
- [x] **2. Functional Verification:**
    - [x] Verify orchestration logic.
    - [x] Verify execution with live Gemini API.
    - [x] Test all tools.
- [x] **3. Codebase Refinement:**
    - [x] Clean up imports.
    - [x] Ensure `requirements.txt` is up-to-date.

### Phase 1.5: Fixes & Critical Improvements
- [x] **1. Agent Capabilities:** (Execution, Security).
- [x] **2. Orchestration Logic:** (Feedback, Persistence, Logging).
- [x] **3. Knowledge Base Integration:** (Inject KB).
- [x] **4. Testing:** (Fix Tool Tests).

### Phase 2: Advanced Research & Foundation Building (Active)
*(Previously Phase 1)*
This phase focuses on systematically researching external systems and refining the agent prompting strategy.

- [x] **1. Analyze Code and Architectural Patterns (`/docs/gitingest/`)**
- [x] **2. Extract Insights from RAG Research Documents (`/docs/research/RAG/`)**
- [x] **3. Audit and Analyze Existing Knowledge Base Files**
- [ ] **4. ArXiv Research Harvesting (In Progress):**
    - [x] Create `urls.txt` and harvesting script.
    - [x] Harvest initial batch of 20+ papers (`docs/articles/`).
    - [x] Create `docs/research_consolidation.md`.
    - [x] Create `docs/khala_ingestion_plan.md`.
    - [x] Harvested 185+ papers (`docs/articles/`).
    - [ ] Complete harvesting of remaining papers.
    - [ ] Ingest research into Khala memory.
- [ ] **5. Reference Repository Analysis (New Task):**
    - [x] Create `repo_urls.txt`.
    - [x] Clone and Analyze `pew-pew-cli` (Harvested: CLI Concepts).
    - [x] Clone and Analyze `pew-pew-workspace` (Harvested: Discovery Phase).
    - [x] Clone and Analyze `droid-factory-template` (Harvested: Agent Personas).
    - [x] Create `docs/agent_integration_strategy.md`.
    - [ ] Clone and Analyze `plandex`.
    - [ ] (Iterate for all 20+ repos).
    - [ ] Generate `docs/references/analysis_[RepoName].md` for each.
    - [ ] Generate `docs/rfcs/rfc_[00X]_integration_[RepoName].md` for each.

### Phase 3: MCP Integration & Specialized Agents
- [x] **1. Evaluate & Prototype MCP Integrations**
- [x] **2. Design & Implement Specialized Support Agents**
- [x] **3. Develop Granular State Management & Logging**

### Phase 4: Workflow Integration & Resilience
- [x] **1. Integrate PlannerAgent**
- [x] **2. Integrate KnowledgeAgent**
- [x] **3. Update Documentation**

### Phase 5: Robustness & Testing Expansion
- [x] **1. Expand Test Suite**
- [x] **2. Fix Test Persistence**
- [x] **3. Enhance MCP Prototype**

### Phase 6: Khala Memory Integration (Completed)
- [x] **1. Integrate Khala Memory System** (SurrealDB + CacheManager).
- [x] **2. Replace mem0 references.**
