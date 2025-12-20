# OpenManus: An Open Source General Agent Framework

## 1. Synthesis

**Repository:** `FoundationAgents/OpenManus`
**Language:** Python
**Core Purpose:** An open-source reproduction of the "Manus" agent, designed to be a versatile, general-purpose autonomous agent capable of solving complex tasks through planning, tool usage, and multi-agent orchestration. It is built by the MetaGPT team.

### Key Capabilities
*   **General Purpose Agent:** Capable of handling open-ended requests (e.g., "Plan a trip to Japan," "Analyze this stock").
*   **Planning & Execution:** Uses a "Flow" architecture (specifically `PlanningFlow`) to break down complex user requests into steps and execute them sequentially.
*   **Tool Ecosystem:** Includes a rich set of built-in tools:
    *   **Browser:** `BrowserUseTool` (headless browser automation via `browser-use`).
    *   **Search:** Google, Bing, Baidu, DuckDuckGo.
    *   **Coding:** `PythonExecute` (sandboxed execution).
    *   **File Ops:** Read/Write/Edit files.
    *   **MCP Support:** Native support for Model Context Protocol to extend capabilities.
*   **Sandboxed Environment:** Executes code and commands in a Docker container for safety.
*   **Multi-Agent Flow:** Supports orchestrating specialized agents (e.g., `DataAnalysisAgent`) alongside the main `Manus` agent.

### Architectural Highlights
*   **`Flow` Abstraction:** The core orchestration logic is wrapped in `Flow` classes (e.g., `BaseFlow`, `PlanningFlow`). This separates the *process* of solving a problem from the *agent* itself.
*   **`Agent` Abstraction:** Agents (`Manus`, `ReActAgent`, `ToolCallAgent`) hold state (memory) and LLM configurations but delegate high-level logic to the Flow.
*   **`Tool` Interface:** Standardized base class for tools, including async support.
*   **Config-Driven:** Extensive use of `config.toml` for swapping LLM providers (OpenAI, Anthropic, Azure, Ollama) and configuring tools.

---

## 2. Strategic Ideas for Golden Armada

OpenManus provides a high-level "General Manager" architecture that complements the specialized squads of the Golden Armada.

### A. The "Planning Flow" Pattern
OpenManus's `PlanningFlow` is superior to a simple ReAct loop for long-horizon tasks.
*   **Idea:** Implement a `MasterPlanSquad` that runs a `PlanningFlow`.
*   **Mechanism:**
    1.  User request -> `MasterPlanSquad`.
    2.  `MasterPlanSquad` generates a 5-step plan.
    3.  Step 1: "Research competitors" -> Delegated to `ReconSquad`.
    4.  Step 2: "Analyze pricing" -> Delegated to `DataSquad`.
    5.  Step 3: "Write report" -> Delegated to `ContentSquad`.
*   **Benefit:** Prevents the "infinite loop" problem common in single-agent architectures.

### B. The "Browser Use" Standard
OpenManus uses the `browser-use` library (which is excellent) wrapped as a tool.
*   **Idea:** Standardize on `browser-use` for the `ReconSquad`'s deep navigation capabilities, enabling agents to interact with modern SPAs (Single Page Apps) just like a human.

### C. Docker Sandbox Manager
OpenManus has a robust `SandboxManager` that spins up Python containers on demand.
*   **Idea:** Adapt this `SandboxManager` for the `CodingSquad`. Instead of just running snippets, the `CodingSquad` should request a *persistent* sandbox session from the Manager, install dependencies, run tests, and keep the environment alive across multiple turns.

---

## 3. Integration Plan (Agno + SurrealDB + Gemini 3)

We will adopt the **Planning Flow** and **Sandbox** concepts.

### Component: `Orchestrator` (The Captain)

#### 1. The `Plan` Graph Node
We will store execution plans in SurrealDB, not just in RAM.
```sql
DEFINE TABLE plan SCHEMAFULL;
DEFINE FIELD goal ON TABLE plan TYPE string;
DEFINE FIELD steps ON TABLE plan TYPE array;
DEFINE FIELD current_step_index ON TABLE plan TYPE number;
DEFINE FIELD status ON TABLE plan TYPE string; -- 'running', 'paused', 'completed'
```

#### 2. The `PlannerAgent` (Agno)
We will create a specialized Agno agent that mimics `PlanningFlow`.
*   **Role:** "Mission Commander".
*   **Instructions:** "You do not execute tasks. You break them down into steps and assign them to Squads."
*   **Output:** Structured JSON plan stored in SurrealDB.

#### 3. Integrating `browser-use`
We will wrap `browser-use` as a FastMCP tool for the Armada.
*   **Reason:** It's Python-native (unlike the Bright Data MCP which is Node.js) and integrates well with our stack.
*   **Implementation:** Create a `BrowserSquad` that uses the `browser-use` library directly to fulfill requests like "Go to Amazon, search for X, and add the first result to cart."

### Implementation Steps

1.  **Sandbox Module:** Port `app/sandbox` from OpenManus to `armada/infrastructure/sandbox`. This gives us instant Docker management.
2.  **Flow Logic:** Port `app/flow/planning.py` logic into the `Orchestrator`'s system prompt and state machine.
3.  **Tool Harvesting:** Extract the `GoogleSearch` and `PythonExecute` tools into our `ArmadaTools` library, as they are well-implemented with async support.

### Refined Workflow: "The Captain's Log"
1.  **User:** "Build a clone of Flappy Bird in Python."
2.  **Captain (Planner):**
    *   Creates Plan:
        1.  Setup environment (Coding Squad).
        2.  Write game logic (Coding Squad).
        3.  Create assets (Design Squad).
        4.  Test (QA Squad).
    *   Writes plan to SurrealDB `plan:flappy_bird`.
3.  **Worker (Coding Squad):**
    *   Sees Step 1.
    *   Request Sandbox from `SandboxManager`.
    *   Executes `pip install pygame`.
    *   Updates Step 1 status to "Complete".
4.  **Captain:**
    *   Sees Step 1 complete.
    *   Activates Step 2.
    *   ...and so on.
