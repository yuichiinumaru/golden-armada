# Reference Analysis: Devika (AI Software Engineer)

**Source:** `gitingest-stitionai-devika.txt`
**Repo:** stitionai/devika
**Date:** 2025-03-31

---

## 1. Synthesis: What is Devika?

Devika is an open-source "Agentic AI Software Engineer" inspired by Devin. It is a sophisticated multi-agent system designed to take high-level objectives, break them down into plans, research technical details, and write code to implement them.

### Core Architecture
Devika uses a **centralized orchestration model** where a main `Agent` class coordinates specialized sub-agents.

*   **Agent Core (`src/agents/agent.py`)**: The brain. It manages state, conversation history, and the execution loop.
*   **Specialized Agents**:
    *   `Planner`: Generates step-by-step plans.
    *   `Researcher`: Search engine integration (Bing/Google) to find docs/solutions.
    *   `Coder`: Writes code based on plans and research.
    *   `Action`: Determines the next move (run, deploy, fix, report).
    *   `Runner`: Executes code in a sandbox.
    *   `Patcher`: Debugs errors.
    *   `Reporter`: Generates PDF reports.
*   **State Management (`src/state.py`)**: Uses SQLModel (SQLite) to persist the "Agent State" (monologue, current step, browser session).
*   **Browser Interaction (`src/browser/`)**: Uses Playwright to read documentation and extract text.

### Key Workflows
1.  **Planning**: `Planner` breaks prompt into steps.
2.  **Research**: `Researcher` generates search queries -> `Browser` visits pages -> `Formatter` extracts content.
3.  **Coding**: `Coder` takes plan + research context -> Outputs file operations.
4.  **Execution**: `Runner` executes the project (e.g., `npm start`, `python main.py`).
5.  **Feedback**: `Patcher` reads error logs and attempts fixes.

---

## 2. Strategic Ideas for CodeSwarm (Golden Armada)

Devika is highly relevant to CodeSwarm because it implements the exact "End-to-End" coding loop we want, but with a different stack (Python/Flask/SQLite vs our Agno/SurrealDB).

### A. The "Monologue" Pattern
Devika's `InternalMonologue` agent generates a stream of consciousness before taking actions.
*   **Idea**: We should explicitize this in our agents. Instead of just "Tool Calls", agents should log "Thoughts" to SurrealDB.
*   **Benefit**: better debugging and "explainability" for the user. "Why did the agent delete that file? Oh, the monologue says it thought it was a duplicate."

### B. The "Browser-Research-Code" Loop
Devika doesn't just "know" things; it looks them up.
*   **Idea**: Our `Developer` agent shouldn't just guess APIs. It should trigger a `Researcher` squad member if it's unsure about a library version.
*   **Mechanism**: If the `Planner` detects "Use Library X", it creates a sub-task "Research Library X docs" before the "Write Code" task.

### C. Project-Based Knowledge Base
Devika creates a `knowledge_base` per project using `SentenceBERT`.
*   **Idea**: We have SurrealDB Vectors. We should create a `ProjectKnowledge` table that stores not just code, but *findings* from the Researcher (e.g., "Found that API v2 is deprecated, use v3"). This prevents re-researching the same facts.

### D. The "Patcher" Agent (Self-Healing)
Devika has a dedicated agent for fixing bugs.
*   **Idea**: In CodeSwarm, the "Revisor" usually reviews *human* or *agent* code. We should add a `Debugger` agent (or mode) that specifically takes *runtime errors* (from the `Runner`) and patches the code.

---

## 3. Integration Plan (Agno + SurrealDB)

We will adopt Devika's **Architecture of Specialization** but implement it using Agno's `Team` or `Squad` structures.

### Phase 1: The `DevikaSquad` Pattern in Agno

We will define a reusable "Coding Squad" pattern inspired by Devika.

**File:** `codeswarm/agno-agents/squads/dev_squad.py`

```python
from agno.agent import Agent
from agno.models.gemini import Gemini
from codeswarm.tools.browser import BrowserToolkit
from codeswarm.tools.fs import FileSystemToolkit

class DevSquad:
    def __init__(self, db_client):
        self.planner = Agent(
            role="Planner",
            model=Gemini(id="gemini-2.0-flash"),
            system_prompt="You are a Technical Planner. Break tasks into atomic coding steps.",
            # ...
        )

        self.researcher = Agent(
            role="Researcher",
            tools=[BrowserToolkit()],
            system_prompt="You are a Documentation Expert. Find API references and usage examples.",
            # ...
        )

        self.coder = Agent(
            role="Coder",
            tools=[FileSystemToolkit()],
            system_prompt="You are a Senior Engineer. Write clean, documented code based on the Plan and Research.",
            # ...
        )

        # The Orchestrator
        self.lead = Agent(
            role="Tech Lead",
            team=[self.planner, self.researcher, self.coder],
            instructions="1. Ask Planner for a plan. 2. Ask Researcher for context. 3. Ask Coder to implement."
        )
```

### Phase 2: State Persistence in SurrealDB

Devika uses `state.py` and SQLite. We will map this to SurrealDB to allow real-time UI updates (Live Query).

**Schema:**
```sql
DEFINE TABLE agent_state SCHEMAFULL;
DEFINE FIELD project_id ON TABLE agent_state TYPE record<project>;
DEFINE FIELD current_step ON TABLE agent_state TYPE string;
DEFINE FIELD internal_monologue ON TABLE agent_state TYPE string;
DEFINE FIELD browser_snapshot ON TABLE agent_state TYPE string; -- URL or HTML summary
DEFINE FIELD status ON TABLE agent_state TYPE string; -- 'thinking', 'coding', 'waiting'
```

### Phase 3: The `KnowledgeBase` Toolkit

We will port the concept of Devika's `src/memory/knowledge_base.py` but use SurrealDB Vector Search.

**File:** `codeswarm/agno-agents/toolkits/knowledge_base.py`

```python
class KnowledgeBaseToolkit(Toolkit):
    def __init__(self, db):
        self.db = db

    def add_finding(self, query: str, content: str):
        """Stores research findings."""
        self.db.create("findings", {
            "query": query,
            "content": content,
            "embedding": self.embed(content)
        })

    def search_findings(self, query: str):
        """Retrieves relevant past research."""
        return self.db.query(
            "SELECT * FROM findings WHERE vector::similarity(embedding, $vec) > 0.8",
            {"vec": self.embed(query)}
        )
```

### Phase 4: Prompt Engineering Adaptation

Devika's Jinja2 prompts (`src/agents/*/prompt.jinja2`) are excellent. We should:
1.  **Extract** the core instructions (e.g., "Write code in this Markdown format...").
2.  **Adapt** them to Agno's system prompt structure.
3.  **Store** them in our `PromptOptimizer` (SPO) system so they can be refined.

**Example Adaptation (Coder Prompt):**
*   *Devika*: "File: `main.py`:\n```py..."
*   *CodeSwarm*: We will enforce this same output format because it's easy to parse deterministically (using `textricator` or regex).

### Summary
Devika validates that a **modular, multi-agent approach** is the right way to build an AI Engineer. We will port its **Roles** (Planner, Researcher, Coder) and **State Model** to our stack, upgrading the storage to SurrealDB and the orchestration to Agno.
