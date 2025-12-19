# CodeSwarm Task List

## DeepCode Integration

### Research & Analysis
- [x] Analyze `HKUDS/DeepCode` repo.
- [x] Generate Analysis Report (`docs/references/DeepCode_analysis.md`).

### Porting: Plan Validation
- [x] **Task 1**: Extract `_assess_output_completeness` from `references/DeepCode/workflows/agent_orchestration_engine.py`.
    - Create `codeswarm/deepcode_utils.py` (serving as validator and parser).
    - Adapted the function to work with CodeSwarm's logging/error handling.
    - Added unit tests to verify it catches bad plans.

### Porting: Plan Parsing
- [x] **Task 2**: Extract `extract_file_tree_from_plan` from `references/DeepCode/workflows/codebase_index_workflow.py`.
    - Integrated into `codeswarm/deepcode_utils.py`.
    - Ensures it can handle Markdown code blocks and raw text.

### Integration: AdminAgent Upgrade
- [x] **Task 3**: Modify `PlannerAgent` (as it handles planning) to use the new Validator and Parser.
    - Updated `planner_prompt.json` to request YAML output (reference `CODE_PLANNING_PROMPT` from DeepCode).
    - Added `run_planner_agent` in `codeswarm/agents.py` with validation loop: If `_assess_output_completeness` < 0.8, reject and retry.

### Integration: DevAgent Prompt Upgrade
- [ ] **Task 4**: Update `DevAgent` system prompt.
    - Adapt `PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT` from DeepCode.
    - Focus on "Single function call per message" and "Build incrementally".

## VulnerableCode Integration

### Research & Analysis
- [x] Analyze `nexB/vulnerablecode` repo.
- [x] Generate Analysis Report (`docs/references/vulnerablecode_analysis.md`).

### Porting: Security Utilities
- [ ] **Task 6**: Port Version Comparison Logic.
    - Add `univers` and `packageurl-python` to `requirements.txt`.
    - Extract `resolve_version_range` from `references/vulnerablecode/vulnerabilities/utils.py`.
    - Create `codeswarm/utils/security.py`.

### Integration: RevisorAgent Upgrade
- [ ] **Task 7**: Add `DependencyCheck` capability to `RevisorAgent`.
    - When reviewing `requirements.txt` or `package.json`, parse dependencies using `packageurl`.
    - (Optional) Check against a local list of known bad versions.

## Context-Engineering Integration

### Research & Analysis
- [x] Analyze `davidkimai/Context-Engineering` repo.
- [x] Generate Analysis Report (`docs/references/Context-Engineering_analysis.md`).

### Porting: Prompts
- [ ] **Task 9**: Create `codeswarm/prompts/verification_loop.md`.
    - Adapt the template from `references/Context-Engineering/20_templates/PROMPTS/verification_loop.md`.
- [ ] **Task 10**: Create `codeswarm/schemas/agent_protocol.json`.
    - Adapt the schema from `references/Context-Engineering/20_templates/PROMPTS/protocol.agent.md`.

### Integration: RevisorAgent Logic
- [ ] **Task 11**: Update `RevisorAgent` logic.
    - Before approving, inject the `verification_loop.md` content into the context.
    - Require the LLM to output "Verification Process" steps.

### Verification
- [ ] **Task 5**: End-to-End Test.
- [ ] **Task 8**: Security Test.
- [ ] **Task 12**: Verification Loop Test.
    - Give `RevisorAgent` a buggy code snippet.
    - Verify it finds the bug using the structured loop.
