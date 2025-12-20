# CrewAI: Flows & Squad Orchestration

## Synthesis
CrewAI is a high-level framework designed for orchestrating "Crews" of role-playing AI agents. It distinguishes itself with two main architectural primitives:
1.  **Crews:** Teams of agents with specific roles (e.g., "Researcher", "Writer") working together on a set of tasks. Execution can be **Sequential** (A -> B -> C) or **Hierarchical** (Manager delegates to A, B, C).
2.  **Flows:** A newer, event-driven architecture that manages the state and execution path between multiple Crews or tasks. It uses decorators (`@start`, `@listen`, `@router`) to define complex, non-linear workflows.

**Key Features:**
*   **Role-Based Design:** Agents are defined by `Role`, `Goal`, and `Backstory`, which effectively "prompts" the LLM to stay in character and context.
*   **Structured Flows:** Flows allow mixing standard Python code with Agent execution, managing state via Pydantic models. This brings engineering rigor (type safety, state management) to agentic workflows.
*   **Memory Systems:** Built-in support for:
    *   *Short-term Memory:* Context of the current execution.
    *   *Long-term Memory:* Persistent database of past executions/learnings (using Chroma/SQLite).
    *   *Entity Memory:* Tracking specific entities (people, companies) across interactions.
*   **Hierarchical Process:** An automatic "Manager" agent can be injected to plan and delegate tasks to worker agents, validating their outputs.

## Strategic Ideas for Golden Armada
CrewAI's "Flows" concept is the missing link in many agent architectures. While Agno handles the *individual* agent well, and SurrealDB handles the *data*, we need a robust way to define the *process*.

1.  **Event-Driven Flows via SurrealDB:** CrewAI's `@listen` decorator is conceptually identical to a SurrealDB **Live Query**. We should build a pythonic wrapper that allows defining agents as listeners to database states.
    *   *CrewAI:* `@listen(task_a_completed)`
    *   *Golden Armada:* `@listen("CREATE task WHERE status='pending'")`
2.  **The "Manager" Pattern:** We should implement a `SquadLeader` agent for each squad. This agent doesn't do the work; it breaks down a user request into sub-tasks (creating `Task` records in DB) and assigns them to specific `Worker` agents (by setting the `assignee` field).
3.  **Structured State:** CrewAI Flows use a Pydantic class to hold the state of the entire flow. We should store this "Flow State" in a `process_state` table in SurrealDB, ensuring that if the system crashes, we can resume the flow from the last saved state.
4.  **Role/Backstory as Configuration:** Instead of hardcoding agent prompts, we should store `AgentProfile` records in SurrealDB containing the `role`, `goal`, and `backstory`. This allows us to "patch" agent behaviors dynamically without redeploying code (a key feature of the "Prompt Engineer Squad").

## Integration Plan (Agno + SurrealDB + Gemini 3)

### 1. The `Flow` Abstraction (Python SDK)
We will create a lightweight SDK that maps Python functions to SurrealDB Live Queries.

```python
class ResearchFlow(Flow):
    state: ResearchState

    @trigger(event="CREATE", table="research_request")
    def start_research(self, payload):
        # Logic to initialize state and spawn initial tasks
        self.db.create("task", {"type": "search", "query": payload.topic})

    @trigger(event="UPDATE", table="task", condition="status='completed'")
    def on_task_complete(self, payload):
        # Logic to aggregate results or trigger next step
        if payload.type == "search":
            self.db.create("task", {"type": "write_report", "data": payload.result})
```

### 2. The Squad Architecture
We will organize our Agno agents into "Squads" that mirror CrewAI's "Crews".

*   **Commander (Meta-Agent):** Receives the user's high-level intent and routes it to the correct Squad (e.g., DevSquad, ResearchSquad).
*   **Squad Leader (Manager):**
    *   Listens for routed requests.
    *   Uses Gemini 3 to decompose the request into a DAG of tasks.
    *   Inserts these tasks into the `tasks` table.
*   **Specialists (Workers):**
    *   Listen for tasks matching their `skill`.
    *   Execute the task using Agno tools.
    *   Update the task record with the result.

### 3. Memory Implementation
*   **Contextual Memory:** Passed in the `messages` list to Gemini.
*   **Long-term Memory:** We will use the Vector Search pattern (defined in the Chroma analysis) to allow agents to query past `TaskResult` records in SurrealDB.
*   **Entity Memory:** A dedicated `entity` table in SurrealDB, linked to `content` via graph edges (`MENTIONS`).

### 4. Why this beats standard CrewAI?
*   **Persistence:** By using SurrealDB as the state store, our "Flows" are durable. CrewAI in-memory flows die if the process dies.
*   **Scale:** We can have 100 `Researcher` agents listening to the task queue. CrewAI crews are typically fixed-size and run on a single machine.
*   **Gemini 3 Native:** We optimize the prompt engineering specifically for Gemini's massive context window, rather than generic OpenAI compatibility.
