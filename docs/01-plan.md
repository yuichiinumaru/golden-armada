# CodeSwarm Master Plan

## Vision
To build a robust, self-correcting multi-agent system capable of autonomous software development, leveraging state-of-the-art techniques from open-source research.

## Integration Strategy: DeepCode (HKUDS)
We have analyzed `HKUDS/DeepCode` and identified key technologies to integrate.

### 1. Robust Planning Protocol
**Problem**: Agents often start coding without a coherent architectural vision, leading to "spaghetti code" or circular dependencies.
**Solution**: Adopt DeepCode's "Plan-First" architecture.
*   **Action**: Implement a strict `PlannerAgent` (or upgrade `AdminAgent`) that produces a comprehensive YAML plan.
*   **Validation**: Port `_assess_output_completeness` to reject malformed or lazy plans.

### 2. Structured Scaffolding
**Problem**: File creation is often ad-hoc.
**Solution**: Use the Plan to drive Scaffolding.
*   **Action**: Port `extract_file_tree_from_plan` to parse the YAML plan and generate `mkdir`/`touch` commands automatically *before* any code is written.

### 3. Context-Aware Reference Mining (Future)
**Problem**: RAG is often too generic.
**Solution**: Structure-Aware Indexing.
*   **Action**: Implement `CodebaseIndexWorkflow` logic to map external references to our intended file structure.

## Roadmap

### Phase 1: The Planner Upgrade
- [ ] Create `PlannerAgent` (or Refactor `AdminAgent`).
- [ ] Implement `_assess_output_completeness`.
- [ ] Define the Standard Plan YAML Schema.

### Phase 2: The Scaffolder
- [ ] Implement `PlanParser` (based on `extract_file_tree_from_plan`).
- [ ] Create a `ScaffoldTool` that takes the plan and creates the directory tree.

### Phase 3: The Execution
- [ ] Update `DevAgent` to consume the Plan YAML instead of vague instructions.
