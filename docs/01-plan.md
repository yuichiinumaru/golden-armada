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

## Integration Strategy: VulnerableCode (nexB)
We have analyzed `nexB/vulnerablecode` and identified key technologies to integrate.

### 1. Supply Chain Security
**Problem**: Generated code may rely on outdated or vulnerable libraries.
**Solution**: "Package-First" Vulnerability Scanning.
*   **Action**: Integrate `univers` and `packageurl-python` libraries.
*   **Implementation**: Create a `SecurityScanner` utility that can resolve version ranges and check `requirements.txt` against safety rules.

## Integration Strategy: Context-Engineering (DavidKimAI)
We have analyzed `davidkimai/Context-Engineering` and identified key technologies to integrate.

### 1. Verification Loops
**Problem**: Agents often hallucinate or make silly logic errors.
**Solution**: Explicit Verification Steps.
*   **Action**: Implement the `Verification Loop` prompt pattern for the `RevisorAgent`.
*   **Effect**: Forces the agent to "Check assumptions" and "Test edge cases" before approving code.

### 2. Rigorous Agent Schemas
**Problem**: Agent definitions are often vague text.
**Solution**: Protocol Schemas.
*   **Action**: Adopt the `protocol.agent` JSON/YAML schema to define agent roles, inputs, and outputs in `AGENTS.md`.

## Roadmap

### Phase 1: The Planner Upgrade (DeepCode)
- [ ] Create `PlannerAgent` (or Refactor `AdminAgent`).
- [ ] Implement `_assess_output_completeness`.
- [ ] Define the Standard Plan YAML Schema.

### Phase 2: The Scaffolder (DeepCode)
- [ ] Implement `PlanParser` (based on `extract_file_tree_from_plan`).
- [ ] Create a `ScaffoldTool` that takes the plan and creates the directory tree.

### Phase 3: The Guardian (VulnerableCode)
- [ ] Integrate `univers` library.
- [ ] Port `resolve_version_range` from VulnerableCode.
- [ ] Create `DependencyCheck` tool for the `RevisorAgent`.

### Phase 4: The Critic (Context-Engineering)
- [ ] Add `verification_loop.md` to prompts.
- [ ] Update `RevisorAgent` system prompt to enforce the loop.

### Phase 5: The Execution
- [ ] Update `DevAgent` to consume the Plan YAML instead of vague instructions.
