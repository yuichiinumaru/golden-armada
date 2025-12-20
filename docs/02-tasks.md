# CodeSwarm Open Tasks

## VulnerableCode Integration (Integration: RevisorAgent Upgrade)
- [ ] **Task 7**: Add `DependencyCheck` capability to `RevisorAgent`.
    - When reviewing `requirements.txt` or `package.json`, parse dependencies using `packageurl`.
    - (Optional) Check against a local list of known bad versions.

## Context-Engineering Integration (Porting: Prompts)
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

## Orchestration & Logic Design (Critical Path)
- [ ] **Task 13**: Design Orchestration Logic.
    - Define routing mechanisms (Semantics vs Registry).
    - Plan `OrchestratorAgent` -> `Armada` delegation.
- [ ] **Task 14**: Implement Orchestration Layer.
    - Update `OrchestratorAgent.py`.
    - Connect to `AgentRegistry`.

## Practical Agent Tests (Critical Path)
- [ ] **Task 15**: Live Agent Swarm Test.
    - Verify User -> Gatekeeper -> Orchestrator -> Specialist flow.
    - Execute a real coding task.
