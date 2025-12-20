# Reference Analysis: Agency Swarm

**Source:** `gitingest-vrsen-agency-swarm (1).txt` & `gitingest-vrsen-agency-swarm-lab.txt`
**Repo:** VRSEN/agency-swarm
**Date:** 2025-03-31

---

## 1. Synthesis: What is Agency Swarm?

Agency Swarm is a Python framework built on top of the **OpenAI Assistants API**. It treats agents not just as LLMs with tools, but as role-based entities in an "Agency" (organization) that communicate via a structured hierarchy.

### Core Concepts

1.  **Agency Structure (`Agency` Class)**:
    *   Defines a DAG (Directed Acyclic Graph) of communication.
    *   `agency_chart = [ceo, [ceo, dev], [ceo, va], [dev, va]]`
    *   Agents can only communicate with those they are explicitly connected to. This prevents "context pollution" and infinite loops.
2.  **Agents (`Agent` Class)**:
    *   Wraps an OpenAI Assistant.
    *   Has `instructions` (System Prompt) and `tools`.
    *   State is managed by OpenAI (Threads), not locally.
3.  **Genesis Agency**:
    *   A meta-agency that creates *other* agencies.
    *   Includes `AgentCreator`, `ToolCreator`, and `OpenAPICreator` agents.
    *   Validates the concept of "Agents building Agents".
4.  **Tools**:
    *   Pydantic-based schemas (similar to Agno).
    *   `SharedState`: A mechanism for tools to share data (e.g., `ad_campaign_id`) without passing it through the LLM conversation context, saving tokens.
5.  **Communication**:
    *   `SendMessage` tool: The primary way agents talk. It transfers the conversation thread to the recipient agent.

### The "Lab" Repository
The `agency-swarm-lab` contains concrete implementations:
*   `MetaMarkAgency`: Facebook Ad automation (CEO -> AdCopy -> ImageCreator -> FBManager).
*   `WebDevCrafters`: Full-stack dev (CEO -> Designer -> Developer -> Copywriter).
*   `CodeGuardians`: PR review system.

---

## 2. Strategic Ideas for CodeSwarm (Golden Armada)

Agency Swarm is the closest architectural cousin to the Golden Armada concept.

### A. Hierarchical Communication Charts
Agno's `Team` is often flat (everyone talks to everyone). Agency Swarm's "Chart" (`[Supervisor, [Supervisor, Worker]]`) is superior for complex tasks.
*   **Idea**: We should enforce strict communication paths in our Squads. A `Planner` talks to `Developer`, but `Developer` might only talk to `Linter` and `Planner`, not `User` directly.

### B. The "Genesis" Pattern
The idea of an agent that *scaffolds* the project structure is powerful.
*   **Idea**: A `CodeSwarmGenesis` agent.
    *   Input: "I need a scraping squad."
    *   Action: Generates `scrapers/squad.py`, `scrapers/tools.py`, and `AGENTS.md` entry.
    *   Benefit: Reduces the boilerplate of adding new capabilities to the Armada.

### C. Shared State vs. Context
Agency Swarm uses `self._shared_state.set("key", value)` in tools.
*   **CodeSwarm Equivalent**: SurrealDB.
    *   Instead of an ephemeral dict, our agents write to the `context` table in SurrealDB.
    *   Tool: `ContextSetter(key="feature_flags", value="{...}")`.
    *   Strategic Value: This creates "Implicit Memory" separate from the "Explicit Memory" (Chat History).

### D. The `SendMessage` Abstraction
Agency Swarm turns communication into a *Tool*.
*   **Idea**: In Agno, we usually just call `agent.print_response()`. We should wrap inter-agent delegation as a tool: `DelegateTask(recipient="Reviewer", instruction="Check this PR")`. This allows the LLM to *decide* when to hand off control.

---

## 3. Integration Plan (Agno + SurrealDB)

We will implement the **Agency Chart** and **Shared State** patterns using Agno's `Team` and SurrealDB.

### Phase 1: The `Agency` Class for Agno

We need a wrapper that enforces the communication graph.

**File:** `codeswarm/agno-agents/orchestrator/agency.py`

```python
class Agency:
    def __init__(self, chart, shared_instructions):
        self.chart = chart
        self.shared_instructions = shared_instructions
        self.agents = self._parse_chart(chart)

    def run(self, initial_prompt):
        # Start with the root agent (CEO/Planner)
        current_agent = self.agents[0]
        response = current_agent.run(initial_prompt)

        # If response includes a 'Delegate' tool call, switch context
        while isinstance(response, DelegateCall):
            next_agent = response.recipient
            response = next_agent.run(response.instruction)
```

### Phase 2: SurrealDB Shared State Toolkit

We will replace Agency Swarm's in-memory `SharedState` with a DB-backed one.

**File:** `codeswarm/agno-agents/toolkits/shared_state.py`

```python
class SharedStateToolkit(Toolkit):
    def __init__(self, db, session_id):
        self.db = db
        self.session_id = session_id

    def set_value(self, key: str, value: str):
        """Stores a value accessible to all agents in this session."""
        self.db.query(
            "UPDATE session SET data[$key] = $value WHERE id = $id",
            {"key": key, "value": value, "id": self.session_id}
        )

    def get_value(self, key: str):
        """Retrieves a value."""
        return self.db.query("SELECT data[$key] FROM session WHERE id = $id")
```

### Phase 3: "Genesis" Agent Implementation

We will create a specialized agent that can generate new agent templates.

**System Prompt:**
"You are the Genesis Agent. Your goal is to generate Python code for new Agno agents based on user requirements. You must follow the `DevSquad` pattern."

**Tool:** `CreateAgentFile(name, role, tools_list)` -> Writes `codeswarm/agents/{name}.py`.

### Detailed Logic Breakdown (Genesis Pattern)

Agency Swarm's `AgentCreator` uses a multi-step process:
1.  **Read Manifesto**: Understand the agency goal.
2.  **Create Template**: Make the folder structure.
3.  **Tool Creation**: Write `tools.py` (we can skip this or use our existing MCP tools).
4.  **Finalize**: Add to `agency.py`.

We will simplify this:
1.  **Input**: "Create a Marketing Squad."
2.  **Action**:
    *   Generate `marketing/copywriter.py` (Agent).
    *   Generate `marketing/designer.py` (Agent).
    *   Generate `marketing/manager.py` (Lead).
    *   Register in `main.py`.

### Conclusion
Agency Swarm teaches us that **structure matters**. Random agents chatting is chaos; a defined hierarchy (Agency Chart) is a "Organization". We will adopt this strict hierarchy to tame the complexity of the Golden Armada.
