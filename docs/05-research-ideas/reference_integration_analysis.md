# Reference Integration Analysis

**Objective**: Identify reusable components from `reference-agno-agents` following the migration of the Golden Armada.

## 1. Structure Comparison

| Component | `reference-agno-agents` | `codeswarm` (Current) | Action |
| :--- | :--- | :--- | :--- |
| **Golden Armada** | `legacy_agents/golden_armada` (Archived) | `agents/armada/` (222 Agents) | **Migrated** |
| **Orchestrator** | `app/agents/orchestrator.py` | *Missing / Basic* | **High Priority Port** |
| **Registry** | `app/services/agent_registry.py` | `factory_agents.py` (Static) | **High Priority Port** |
| **BI Suite** | `app/agents/bi_*.py` (5 agents) | *Missing* | **Recommend Porting** |
| **Fiscal Suite** | `app/agents/fiscal_*.py` (4 agents) | *Missing* | **Recommend Porting** |
| **Legal Suite** | `app/agents/legal_*.py` (2 agents) | *Missing* | **Recommend Porting** |
| **Location Suite** | `app/agents/location_*.py` | *Missing* | **Recommend Porting** |
| **Deep Reasoner** | `app/agents/deepreasoner.py` | *Missing* | **Evaluate** |

## 2. Key Findings

### A. The Orchestrator
The reference `OrchestratorAgent` (`app/agents/orchestrator.py`) is sophisticated.
- **Capabilities**:
    - `plan_workflow(request)`: Generates JSON execution plans with `single` or `parallel` steps.
    - `review_task_output()`: Self-correction loop.
    - `generate_final_report()`: Executive summary generation.
- **Dependencies**: It relies on `KhalaBaseAgent` (now `SwarmAgent`) and Pydantic models.
- **Integration**: It is compatible with the new `SwarmAgent` class with minor refactoring.

### B. The Registry
The reference `AgentRegistry` (`app/services/agent_registry.py`) uses dynamic loading to find agents.
- **Value**: `codeswarm` currently uses `factory_agents.py` which requires manual registration.
- **Recommendation**: Port the dynamic registry logic to automatically load the 222 agents in `codeswarm/agents/armada/`. This avoids maintaining a 222-line import list.

### C. Specialist Suites
Multiple "Application-Level" agents exist that offer higher-level logic than the "Role-Based" Armada agents.
- **BI Suite**: `Analyst`, `Architect`, `Detective`, `Janitor`. Good for data tasks.
- **Fiscal Suite**: `Accuser`, `Defender`, `Judge`, `Scout`. Good for auditing/finance logic.
- **Legal/Location**: specialized domain logic.

## 3. Recommendations

1.  **Port Orchestrator**: Create `codeswarm/agents/orchestrator_agent.py` based on the reference. This will be the "Brain" that controls the "Armada".
2.  **Port Registry**: Create `codeswarm/core/registry.py` to dynamically load the Armada.
3.  **Port Specialists**: Move the BI/Fiscal/Legal suites to `codeswarm/agents/specialists/`.
4.  **Deep Reasoner**: Port as `codeswarm/agents/reasoning_agent.py` for complex chain-of-thought tasks.
