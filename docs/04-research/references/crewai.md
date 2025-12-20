# Reference Analysis: CrewAI

## 1. Synthesis

**CrewAI** is a high-level Python framework for orchestrating role-playing, autonomous AI agents. Unlike lower-level frameworks that focus on individual agent loops or pure prompt engineering, CrewAI is designed around the concept of a **"Crew"**—a team of agents working together to achieve a common goal.

### Core Value Proposition
CrewAI abstracts the complexity of multi-agent systems into a familiar team-based structure. It emphasizes:
1.  **Role-Playing**: Agents have specific `roles`, `goals`, and `backstories` (e.g., "Senior Researcher", "Reporting Analyst").
2.  **Collaboration**: Agents can delegate tasks to each other or work sequentially/hierarchically.
3.  **Process Management**: It provides structured "Processes" (Sequential, Hierarchical) to control how tasks are executed.
4.  **Production Readiness**: Includes features for memory (short-term, long-term, entity), observability (telemetry, tracing), and human-in-the-loop interaction.

### Key Features
*   **Agents**: Standalone entities with defined personas and tools.
*   **Tasks**: Specific units of work assigned to agents, with descriptions and expected outputs.
*   **Crews**: The container that binds agents and tasks together with a specific process.
*   **Processes**:
    *   **Sequential**: Tasks are executed one after another.
    *   **Hierarchical**: A "Manager" agent (often powered by a stronger LLM) assigns tasks and reviews work.
*   **Flows**: A newer feature for event-driven workflows (state machines), allowing for more complex, branching logic compared to the linear Crew structure.
*   **Memory System**: sophisticated memory including Contextual, Entity, and Long-Term memory (using vector stores like ChromaDB).
*   **Output Handling**: Supports structured output (Pydantic models, JSON) and file saving.

### Architectural Components
The codebase is organized into several key modules under `src/crewai/`:
*   **`agent.py`**: Defines the `Agent` class, handling LLM interaction, tool usage, and memory updates.
*   **`task.py`**: Defines `Task`, connecting agents to specific goals.
*   **`crew.py`**: The orchestrator. Manages the lifecycle of a run, kicking off agents, and handling data flow.
*   **`process.py`**: Enums and logic for different execution modes.
*   **`memory/`**: A complex subsystem with storage adapters (`ltm_sqlite_storage.py`, `rag_storage.py`) and memory types (`short_term`, `long_term`, `entity`).
*   **`tools/`**: Integration with `crewai-tools` (analyzed in the previous report).
*   **`flow/`**: Implementation of the new Flows architecture (`@start`, `@listen`, `@router` decorators).

---

## 2. Strategic & Architectural Ideas for CodeSwarm

**CodeSwarm** (Agno + SurrealDB + Gemini 3) aims to be a "Golden Armada" of coding agents. CrewAI is the closest direct competitor/reference in terms of high-level abstraction. We should adopt its best patterns while leveraging our superior tech stack (SurrealDB vs SQLite/Chroma).

### 2.1. The "Crew" Abstraction (Golden Armada)
CodeSwarm currently has "Agents" but lacks a strong "Team" concept.
*   **Idea**: Implement a `Swarm` or `Squad` class in Agno.
*   **Application**: A "Frontend Squad" might consist of a `ReactDev`, `CSSExpert`, and `UXReviewer`. An "Infrastructure Squad" has `TerraformDev` and `SecurityAuditor`.
*   **Benefit**: This allows us to scale. The `AdminAgent` doesn't manage 50 agents; it manages 5 Squad Leaders.

### 2.2. Structured "Process" Management
CrewAI's distinction between `Sequential` and `Hierarchical` processes is powerful.
*   **Idea**: Explicitly define execution strategies in CodeSwarm.
*   **Current State**: CodeSwarm mostly does "Manager delegates to Worker".
*   **Improvement**: We should support a **"Peer Review Process"** (Worker -> Reviewer -> Worker) and a **"Brainstorming Process"** (Multiple Workers -> Synthesizer).

### 2.3. The Memory Subsystem (SurrealDB Advantage)
CrewAI uses RAG (Chroma/Mem0) for long-term memory. CodeSwarm has SurrealDB.
*   **Strategic Advantage**: SurrealDB is *both* a graph and a vector DB. We can do better than CrewAI.
*   **Idea**: `EntityMemory`. CrewAI extracts entities and stores them. We can map these directly to SurrealDB Graph Nodes (`User`, `Task`, `File`, `Concept`).
*   **Implementation**: When an agent learns "The login API changed", it shouldn't just vector-store that text. It should update the `API_Endpoint` node in the graph.

### 2.4. Flows (Event-Driven Architecture)
CrewAI's new `Flows` feature (using decorators like `@listen`) is very similar to "LangGraph" but simpler.
*   **CodeSwarm Fit**: Agno has `Workflows`. We should ensure our workflows support event-driven triggers ("Code Pushed" -> "Run Tests").

### 2.5. Task Output Standardization
CrewAI Tasks have `expected_output` and `pydantic` output formats.
*   **Requirement**: Every CodeSwarm task *must* produce a structured artifact (e.g., a `CodeChangeRequest` object), not just a chat message. This makes the system deterministic.

---

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

We will implement the "Squad" architecture and advanced memory.

### 3.1. Stack Mapping

| Component | CrewAI | CodeSwarm Target | Notes |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | `Crew` class | **Agno `Team` / `Workflow`** | Agno has a `Team` concept; we should extend it. |
| **Agent Config** | YAML (`agents.yaml`) | **SurrealDB + TOML** | We prefer DB-backed config for dynamic updates. |
| **Memory** | ChromaDB + SQLite | **SurrealDB** | All-in-one state store. |
| **LLM** | LiteLLM | **Gemini 1.5 Pro** | Native multimodal and huge context. |

### 3.2. Data Model (SurrealDB)

We need schema to support the "Squad" concept.

**Table: `squads`**
```sql
DEFINE TABLE squads SCHEMAFULL;
DEFINE FIELD name ON squads TYPE string;
DEFINE FIELD mission ON squads TYPE string;
DEFINE FIELD process ON squads TYPE string; -- 'sequential', 'hierarchical', 'collaborative'
DEFINE FIELD members ON squads TYPE array<record(agents)>;
DEFINE FIELD created_at ON squads TYPE datetime DEFAULT time::now();
```

**Table: `memories`** (The replacement for CrewAI's complex memory system)
```sql
DEFINE TABLE memories SCHEMAFULL;
DEFINE FIELD agent_id ON memories TYPE record(agents);
DEFINE FIELD type ON memories TYPE string; -- 'short_term', 'long_term', 'entity'
DEFINE FIELD content ON memories TYPE string;
DEFINE FIELD embedding ON memories TYPE array<float>;
DEFINE FIELD metadata ON memories TYPE object;
DEFINE INDEX idx_embedding ON memories FIELDS embedding MTREE DIMENSION 768 DIST COSINE;
```

### 3.3. Agno Agent Implementation

We will create a `Squad` class that wraps Agno Agents.

```python
from typing import List
from agno.agent import Agent, Team

class Squad:
    def __init__(self, name: str, agents: List[Agent], process: str = "sequential"):
        self.name = name
        self.process = process
        # Agno's Team handles the actual LLM coordination
        self.team = Team(
            name=name,
            agents=agents,
            description=f"A squad dedicated to {name}",
            instructions=self._get_process_instructions()
        )

    def _get_process_instructions(self) -> str:
        if self.process == "sequential":
            return "Pass tasks one by one. Do not parallelize."
        elif self.process == "hierarchical":
            return "The Leader (first agent) assigns tasks to others and reviews output."
        return "Collaborate freely."

    def run(self, task: str):
        return self.team.run(task)
```

#### Step 2: The Memory Tool (Contextual)
A tool that Agents use to recall past interactions.

```python
from agno.tools import Toolkit

class MemoryToolkit(Toolkit):
    def save_insight(self, content: str):
        """Saves a key learning or fact to long-term memory."""
        # Insert into SurrealDB 'memories'
        pass

    def recall(self, query: str):
        """Searches long-term memory."""
        # Vector search in SurrealDB
        pass
```

---

## 4. Specific Implementation Steps

### Phase 1: The Squad Abstraction
1.  **File**: `codeswarm/core/squad.py`.
2.  **Logic**: Implement the `Squad` class wrapping Agno's `Team`.
3.  **Config**: Create `codeswarm/config/squads.yaml` to define standard squads (e.g., "BackendSquad", "QA_Squad").

### Phase 2: Memory Integration
4.  **Tool**: `codeswarm/tools/memory.py`.
5.  **Agent Update**: All `SwarmAgent` instances get the `MemoryToolkit` by default.
6.  **Schema**: Apply the `memories` table schema to SurrealDB.

### Phase 3: Task Standardization
7.  **Model**: Define `TaskResult` (Pydantic) in `codeswarm/core/types.py`.
8.  **Enforcement**: Agents must return `TaskResult` (using Gemini's structured output mode).

### Phase 4: Observability (Telemetry)
9.  CrewAI has extensive telemetry (`telemetry.py`). We should add a simple logging hook in `codeswarm/core/event_logger.py` that pushes run stats to SurrealDB (`run_logs` table) for dashboarding.

## 5. Detailed Logic Breakdown (from Source)

### 5.1. `crew.py` - Kickoff
*   **Kickoff**: The entry point. It accepts `inputs` (dict) and interpolates them into the agent's prompt.
*   **Loop**: Iterates through `tasks`.
*   **Delegation**: If delegation is enabled, agents can call a `DelegateWork` tool.
*   **CodeSwarm Note**: We need to support variable interpolation in prompts (`{topic}`) to make agents reusable.

### 5.2. `agents/parser.py`
*   **Parsing**: CrewAI uses a robust parser to handle LLM outputs (Thought/Action/Observation).
*   **ReAct**: It implements the ReAct loop strictly.
*   **Agno**: Agno handles this natively, but we should ensure our prompts encourage "Thought" steps to improve reasoning.

### 5.3. `memory/contextual/contextual_memory.py`
*   **Logic**: Uses a sliding window or vector search to fetch *relevant* past context for the current task.
*   **Importance**: This is crucial for maintaining coherence in long conversations.

## 6. Conclusion

CrewAI is the "Django" of agent frameworks—batteries included, opinionated, and structured. CodeSwarm is building a similar system but with a more modern, data-centric stack (Agno + SurrealDB). The key takeaways are: **Structure your agents into Teams (Squads)**, **Formalize the Task Hand-off (Process)**, and **Treat Memory as a First-Class Citizen** (using SurrealDB's vector powers).
