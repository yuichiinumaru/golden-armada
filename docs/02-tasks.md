# CodeSwarm Task List

## DeepCode Integration

### Research & Analysis
- [x] Analyze `HKUDS/DeepCode` repo.
- [x] Generate Analysis Report (`docs/references/DeepCode_analysis.md`).

### Porting: Plan Validation
- [ ] **Task 1**: Extract `_assess_output_completeness` from `references/DeepCode/workflows/agent_orchestration_engine.py`.
    - Create `codeswarm/utils/plan_validator.py`.
    - Adapt the function to work with CodeSwarm's logging/error handling.
    - Add unit tests to verify it catches bad plans.

### Porting: Plan Parsing
- [ ] **Task 2**: Extract `extract_file_tree_from_plan` from `references/DeepCode/workflows/codebase_index_workflow.py`.
    - Create `codeswarm/utils/plan_parser.py`.
    - Ensure it can handle Markdown code blocks and raw text.

### Integration: AdminAgent Upgrade
- [ ] **Task 3**: Modify `AdminAgent` to use the new Validator and Parser.
    - Update prompt to request YAML output (reference `CODE_PLANNING_PROMPT` from DeepCode).
    - Add a validation loop: If `_assess_output_completeness` < 0.8, reject and retry.
    - Add a scaffolding step: Parse plan -> Create files.

### Integration: DevAgent Prompt Upgrade
- [ ] **Task 4**: Update `DevAgent` system prompt.
    - Adapt `PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT` from DeepCode.
    - Focus on "Single function call per message" and "Build incrementally".

### Verification
- [ ] **Task 5**: End-to-End Test.
    - Run CodeSwarm on a sample task (e.g., "Create a Snake game").
    - Verify it generates a `plan.yaml`.
    - Verify the file structure is created automatically.
    - Verify `DevAgent` follows the new rigorous protocol.
