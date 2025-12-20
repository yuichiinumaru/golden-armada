# Reference Analysis: OpenManus

## 1. Synthesis

**OpenManus** is an open-source reimplementation of "Manus" (a generalist AI agent known for high autonomy), built by contributors from the MetaGPT team. It positions itself as a "versatile agent that can solve various tasks using multiple tools" without requiring an invite code.

### Core Value Proposition
OpenManus provides a **Generalist Agent** architecture that isn't hardcoded for a specific domain (like coding or writing). Instead, it uses a planning-execution loop to solve open-ended problems (e.g., "Plan a trip to Japan," "Analyze this stock market data").

### Key Features
*   **Planning-Execution Architecture**: It doesn't just react; it plans. It includes a `PlanningFlow` that breaks tasks into steps and executes them.
*   **Tool-Use Centric**: Built heavily around tool invocation. It integrates:
    *   **Browser Use**: Native support for `browser-use` (headless browser automation) to read web pages.
    *   **Google Search**: Uses `googlesearch-python`.
    *   **File Operations**: Standard read/write capabilities.
    *   **Python Execution**: Can write and run Python scripts (with safety measures).
    *   **MCP Support**: Can connect to Model Context Protocol servers.
*   **Multi-Agent Flow**: Supports a `Flow` concept where different agents (e.g., `Manus` vs `DataAnalysis`) can be orchestrated.
*   **Simple Configuration**: Uses TOML files for configuration (`config.toml`).

### Architectural Components
The codebase is Python-based (`app/`).
*   **`app/agent/`**: Contains agent implementations.
    *   `base.py`: The abstract base class.
    *   `manus.py`: The flagship generalist agent.
    *   `toolcall.py`: An agent specialized in calling tools.
*   **`app/flow/`**: Defines workflows. `planning.py` implements the "Plan -> Execute" loop.
*   **`app/tool/`**: The tool implementations.
*   **`app/llm.py`**: A wrapper around OpenAI/Azure/Ollama clients, handling token counting and retries.
*   **`run_flow.py`**: The entry point for multi-agent execution.

---

## 2. Strategic & Architectural Ideas for CodeSwarm

**CodeSwarm** is currently focused on *coding*. OpenManus demonstrates how to build *general* autonomy.

### 2.1. The "Manus" Planning Pattern
OpenManus separates the **Planner** from the **Executor**.
*   **Idea**: CodeSwarm has a `PlannerAgent`, but it's often static. We should adopt the **dynamic re-planning** loop.
*   **Implementation**: After every step, the agent checks "Is the plan still valid?". If it encounters an error, it updates the plan, rather than just retrying the tool.

### 2.2. Tool Collection Abstraction
`app/tool/tool_collection.py` provides a clean way to manage tools.
*   **Idea**: CodeSwarm currently passes list of tools manually. We should have a `ToolRegistry` in SurrealDB that agents query at runtime based on their current sub-task.

### 2.3. Browser Use Integration
OpenManus uses the `browser-use` library (based on Playwright).
*   **Strategic Validation**: This confirms our decision (from the `brightdata-mcp` report) that headless browser automation is a standard requirement for modern agents. CodeSwarm *must* have this to check documentation and verify frontend deployments.

### 2.4. Python Execution as a Tool, Not Just a Goal
OpenManus treats `python_execute` as just another tool to get information (e.g., "Run this script to calculate the stock average").
*   **CodeSwarm Shift**: Currently, CodeSwarm writes code to *files*. It should also be able to write *ephemeral* code to answer questions about the codebase (e.g., "Write a script to count how many functions are in `src/`").

---

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

We will integrate the "Generalist" capabilities into CodeSwarm.

### 3.1. Stack Mapping

| Component | OpenManus | CodeSwarm Target | Notes |
| :--- | :--- | :--- | :--- |
| **Agent Base** | Custom `BaseAgent` | **Agno `Agent`** | Agno provides the loop; we provide the brain. |
| **Orchestrator** | `Flow` | **Agno `Workflow`** | |
| **Tools** | Custom Classes | **Agno Toolkit** | |
| **State** | In-Memory | **SurrealDB** | Persistent state allows "Long-Running Manus". |

### 3.2. Data Model (SurrealDB)

We need to store the *Plan* state persistently.

**Table: `plans`**
```sql
DEFINE TABLE plans SCHEMAFULL;
DEFINE FIELD task_id ON plans TYPE record(tasks);
DEFINE FIELD steps ON plans TYPE array;
DEFINE FIELD current_step_index ON plans TYPE int;
DEFINE FIELD status ON plans TYPE string;
DEFINE FIELD created_at ON plans TYPE datetime DEFAULT time::now();
```

### 3.3. Agno Agent Implementation

We will create a `PlannerAgent` that mimics the OpenManus logic.

```python
from agno.agent import Agent
from codeswarm.tools.surreal_store import SurrealStore

class PlannerAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Planner",
            instructions="""
            1. Analyze the user request.
            2. Break it down into step-by-step instructions.
            3. Store the plan in the database.
            4. As the DeveloperAgent executes, update the plan status.
            """
        )
```

#### Step 2: The Tool Call Agent
OpenManus has a dedicated `ToolCallAgent`. In Agno, every agent is a tool call agent, but we can specialize one for *research*.

```python
from agno.agent import Agent
from codeswarm.tools.web_search import WebSurferToolkit # From previous report

researcher = Agent(
    role="Researcher",
    tools=[WebSurferToolkit()],
    description="I find information to unblock the Developer."
)
```

---

## 4. Specific Implementation Steps

### Phase 1: Planning Loop
1.  **Create**: `codeswarm/agents/specialized/planner.py`.
2.  **Logic**: Implement the "Breakdown -> Execute -> Review" loop.
3.  **Schema**: Create `plans` table in SurrealDB.

### Phase 2: Browser Tool Integration
4.  **Dependency**: Add `browser-use` to `requirements.txt` (it's a high-level wrapper around Playwright, easier than raw Playwright).
5.  **Tool**: `codeswarm/tools/browser.py`.

### Phase 3: The "Generalist" Mode
6.  **Update `main.py`**: Add a `--mode=general` flag that launches a `Manus`-like agent instead of the strict coding workflow. This allows CodeSwarm to handle requests like "Research this library and tell me if we should use it".

## 5. Detailed Logic Breakdown (from Source)

### 5.1. `app/flow/planning.py`
*   **Logic**:
    *   `execute()`: Main loop.
    *   `create_plan()`: Calls LLM to generate steps.
    *   `execute_step()`: Delegates to specific agents based on step type.
    *   **Insight**: The `flow` abstraction is useful. It's not just one agent; it's a state machine driving agents.

### 5.2. `app/tool/python_execute.py`
*   **Safety**: OpenManus runs Python code. It has a `NormalPythonExecute` class.
*   **Output Capture**: It captures `stdout` to feed back into the context.

## 6. Conclusion

OpenManus proves that a **Planning-First** architecture yields better results for complex tasks than a simple "React" loop. CodeSwarm should adopt this by making the `PlannerAgent` the "Captain" of the squad, maintaining a persistent plan in SurrealDB that guides the other agents (Developer, Reviewer) through multi-step coding sagas.
