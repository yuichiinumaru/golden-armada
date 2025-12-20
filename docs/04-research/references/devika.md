# Devika: The Open-Source AI Software Engineer

## 1. Synthesis

**Repository:** `stitionai/devika`
**Language:** Python
**Core Purpose:** An open-source alternative to "Devin", designed as an autonomous AI software engineer capable of understanding high-level instructions, planning, researching, coding, and fixing bugs.

### Key Capabilities
*   **Multi-Agent Architecture:** Decomposes software engineering into specialized roles:
    *   `Planner`: Breaks tasks into steps.
    *   `Researcher`: Searches the web for documentation/solutions.
    *   `Coder`: Writes code in multiple languages.
    *   `Runner`: Executes code in a sandboxed environment.
    *   `Patcher`: Fixes bugs based on error output.
    *   `Reporter`: Generates documentation.
*   **Project Management:** Persistent state management (SQLModel/SQLite) allows pausing and resuming complex tasks.
*   **Browser Interaction:** Uses Playwright to browse the web, extract content, and take screenshots for visual context.
*   **Dynamic State Tracking:** Maintains a real-time "Monologue" and state stack, visible to the user via a UI.

### Architectural Highlights
*   **Jinja2 Prompts:** extensively uses Jinja2 templates for structured prompting of LLMs.
*   **Event-Driven:** Uses Socket.IO to stream agent thoughts, code generation, and terminal output to the frontend in real-time.
*   **Modularity:** Each agent (`Coder`, `Planner`) is a standalone class with a standardized `execute()` method and specific prompt templates.

---

## 2. Strategic Ideas for Golden Armada

Devika offers a "Squad-in-a-Box" architecture that aligns perfectly with the Golden Armada's goals.

### A. Specialized Agent Classes (The "Persona" Pattern)
Devika explicitly separates `Coder` from `Planner` from `Researcher`.
*   **Idea:** Adopt this strict separation for Agno agents.
*   **Benefit:** Keeps context windows clean. The `Coder` doesn't need to see the `Researcher`'s 50 pages of search results, only the summarized findings.

### B. The "Internal Monologue" UI
Devika streams the agent's "thoughts" to the UI before acting.
*   **Idea:** Implement a `ThoughtStream` graph node in SurrealDB.
*   **Mechanism:** When an agent thinks (using the `<think>` tag or internal logic), it pushes a record to `thought_stream`. The frontend subscribes to this table via Live Queries to show a "Matrix-style" feed of the Armada's cognition.

### C. Self-Healing Code Loop (`Patcher` Agent)
Devika's `Patcher` agent takes code + error -> new code.
*   **Idea:** Create a `DebugLoop` tool.
*   **Logic:**
    1.  `CodingSquad` writes code.
    2.  `ExecutionSquad` runs it.
    3.  If exit code != 0, pass `stderr` to `DebugSquad`.
    4.  `DebugSquad` modifies the file.
    5.  Repeat (Max 3 retries).

---

## 3. Integration Plan (Agno + SurrealDB + Gemini 3)

We will adopt the **Multi-Agent State Machine** concept.

### Component: `SquadCoordinator`

#### 1. State Persistence in SurrealDB
Devika uses SQLite. We will use SurrealDB to store the *entire* state stack of an ongoing mission.
```sql
DEFINE TABLE mission_state SCHEMAFULL;
DEFINE FIELD project_name ON TABLE mission_state TYPE string;
DEFINE FIELD current_step ON TABLE mission_state TYPE number;
DEFINE FIELD agent_monologue ON TABLE mission_state TYPE string;
DEFINE FIELD browser_snapshot ON TABLE mission_state TYPE string;
```

#### 2. The `ContextSwitch` Pattern
Devika passes context between agents explicitly.
*   **Implementation:** When `Planner` finishes, it writes a `Plan` object to the Graph. The `Coder` agent is triggered (via Live Query) only when a `Plan` node is linked to the `Project` node.
*   **Prompting:** We will port Devika's excellent Jinja2 prompts (especially `coder/prompt.jinja2`) into our `Agno` agent instructions, adapting them for Gemini's large context window.

#### 3. Browser-Augmented Coding
Devika uses a browser to look up docs *while* coding.
*   **Workflow:**
    1.  `CodingSquad` encounters an unknown library error.
    2.  Instead of guessing, it emits a `ResearchRequest` event.
    3.  `ReconSquad` (using Bright Data or Browser Use) finds the docs.
    4.  `ReconSquad` inserts a `Documentation` node into the Knowledge Graph.
    5.  `CodingSquad` is notified, reads the doc, and fixes the code.

### Implementation Steps

1.  **Prompt Porting:** Copy the logic from `src/agents/*/prompt.jinja2` and convert them into Agno system prompts. They are high-quality, task-specific prompts.
2.  **State Schema:** Define the `Mission` and `State` tables in SurrealDB to mirror Devika's state tracking.
3.  **UI Feedback:** Ensure the Golden Armada's API exposes the "Internal Monologue" stream so users trust the autonomous process.

### Refined Workflow: "The Self-Correction Loop"
1.  **User:** "Fix the bug in `auth.py`."
2.  **Orchestrator:** Activates `PatcherSquad`.
3.  **Patcher:**
    *   Reads `auth.py`.
    *   Runs tests -> Fails.
    *   *Self-Correction:* "I need to see the logs."
    *   Reads logs.
    *   Applies patch.
    *   Runs tests -> Passes.
4.  **Orchestrator:** Marks task complete.
