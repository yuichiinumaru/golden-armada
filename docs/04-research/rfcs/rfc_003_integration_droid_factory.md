# RFC 003: Dynamic Agent Personas (Droid Factory)

## Objective
Enable CodeSwarm to instantiate specialized agents ("Personas") dynamically, rather than relying on a fixed set of generic agents (Dev, Revisor). This allows the swarm to adapt to the task at hand (e.g., spawning a `security-auditor` for a sensitive module).

## Proposed Changes

### 1. Persona Library
*   Create `codeswarm/personas/` directory.
*   Import selected "Droid" definitions from `droid-factory-template` (converted to compatible format or kept as markdown).

### 2. Persona Loader
*   Create `codeswarm/utils/persona_loader.py`.
*   Function `load_persona(name: str) -> str`: Reads the markdown file and extracts the system instructions.

### 3. Agent Factory Enhancement
*   Modify `agents.py`: `get_specialized_agent(role: str, model_id: str) -> Agent`.
*   This function loads the persona instructions and injects them into the Agno Agent.

### 4. Planner Integration
*   Update `PlannerAgent` prompt to allow it to *request* specific personas for the next round.
    *   *Example:* "For the next round, assign Task 1 to a `backend-architect` persona."

## Implementation Steps (Checklist)

1.  [ ] **Harvest:** Copy `droids/` to `codeswarm/personas/`.
2.  [ ] **Loader:** Implement `persona_loader.py`.
3.  [ ] **Factory:** Implement `get_specialized_agent` in `codeswarm/agents.py`.
4.  [ ] **Prompt:** Update `planner_prompt.json` to list available personas.
