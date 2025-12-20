# RFC 002: Discovery Phase and Template-Driven Workflow

## Objective
Adopt the "Discovery Phase" and "Template-Driven" patterns from `pew-pew-workspace` to enhance CodeSwarm's ability to handle ambiguous project goals. Currently, CodeSwarm assumes a clear `goal`. We need a phase to *refine* the goal before Planning.

## Proposed Changes

### 1. New Agent: DiscoveryAgent
*   **Role:** Clarify user intent, brainstorm ideas, and produce a refined Project Goal.
*   **Input:** Raw user request ("I want a game").
*   **Output:** `RefinedGoal` (Structured).

### 2. Template System
*   Create `codeswarm/templates/` to store markdown templates (e.g., `idea_template.md`, `prd_template.md`).
*   Agents should be instructed to "fill out" these templates rather than just outputting free text.

### 3. AgentOS Update
*   Insert `_discovery_phase()` before `_strategic_planning_phase()`.
*   If the goal is vague, `DiscoveryAgent` engages the user (via `request_user_input` or simulation).

## Implementation Steps (Checklist)

1.  [ ] **Harvest:** Copy useful templates from `pew-pew-workspace/templates` to `codeswarm/templates/`.
2.  [ ] **Agent:** Create `DiscoveryAgent` in `codeswarm/agents.py`.
3.  [ ] **OS:** Update `AgentOS` to support `Discovery` phase.
4.  [ ] **Prompting:** Update `admin_prompt.json` to respect the outputs of the Discovery phase.
