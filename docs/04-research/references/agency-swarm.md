# Agency Swarm: Hierarchical Agent Orchestration

## 1. Synthesis

**Repository:** `VRSEN/agency-swarm`
**Language:** Python
**Core Purpose:** An agent orchestration framework built on top of the OpenAI Assistants API. It allows users to create collaborative swarms of agents (Agencies) with distinct roles, capabilities, and hierarchical communication flows.

### Key Capabilities
*   **Agency & Agents:** Defines an `Agency` as a collection of `Agents` (CEO, Developer, Virtual Assistant) with directed communication flows (e.g., CEO -> Developer).
*   **OpenAI Assistants API Wrapper:** Abstracts the complexity of managing Assistants, Threads, and Runs. It handles tool execution and message history automatically.
*   **Tooling:** Provides a `BaseTool` class (Pydantic-based) for creating custom tools with automatic schema generation for OpenAI function calling.
*   **Communication:** Agents communicate via a special `SendMessage` tool, which is dynamically generated based on the agency chart.
*   **Genesis Agency:** A meta-agency that can create *other* agencies. It includes agents like `GenesisCEO`, `AgentCreator`, and `ToolCreator`.

### Architectural Highlights
*   **`Agency` Class:** The main entry point. It takes an `agency_chart` (list of agents and communication links) and initializes the thread management.
*   **Directed Acyclic Graph (DAG) Communication:** Communication is defined directionally. If `[CEO, Developer]` is defined, CEO can message Developer, but Developer cannot initiate new tasks for CEO (only respond).
*   **State Management:** Uses `shared_state` to pass data between tools and agents without using context window tokens.
*   **Gradia/Terminal Demo:** Built-in methods to run the agency in a web UI or terminal for testing.

---

## 2. Strategic Ideas for Golden Armada

Agency Swarm provides a robust model for *structured* multi-agent collaboration, which is essential for the Armada's "Squad" concept.

### A. The "Squad Chart"
Agency Swarm's `agency_chart` is the perfect data structure for defining a Squad.
*   **Idea:** Define `Squad` configurations in SurrealDB using a similar schema.
*   **Example:** `ContentSquad = [EditorInChief, [EditorInChief, Writer], [Writer, Researcher]]`.
*   **Benefit:** Strict hierarchy prevents chaos. The `EditorInChief` controls the flow, while `Writer` and `Researcher` focus on execution.

### B. The `Genesis` Pattern (Meta-Agent)
The "Genesis Agency" capability (agents creating agents) is the ultimate goal of the Golden Armada.
*   **Idea:** Implement a `RecruitmentSquad`.
*   **Function:** When a user says "I need a team to build a mobile app," the `RecruitmentSquad` analyzes the request and instantiates a new `MobileDevSquad` with the correct roles (iOS Dev, Android Dev, UX Designer) and tools, essentially "hiring" the right agents from the database.

### C. Type-Safe Tools via Pydantic
Agency Swarm enforces Pydantic for all tools. This matches our finding from `fastapi-mcp`.
*   **Idea:** Standardize all Armada tools on the `BaseTool` pattern. Every tool must have a strict schema, which allows us to auto-generate UIs and API docs.

---

## 3. Integration Plan (Agno + SurrealDB + Gemini 3)

We will adapt the **Communication Hierarchy** and **Genesis** concepts.

### Component: `SquadManager`

#### 1. Defining Hierarchies in SurrealDB
We need a graph structure to represent permission to speak.
```sql
DEFINE TABLE agent SCHEMAFULL;
DEFINE TABLE can_message SCHEMAFULL; -- Edge table

-- CEO can message Developer
RELATE agent:ceo->can_message->agent:developer;
```

#### 2. The `SendMessage` Tool (Agno Port)
We will port the `SendMessage` tool logic to Agno.
*   **Logic:** When Agent A wants to talk to Agent B, it calls `send_message(recipient="Agent B", content="...")`.
*   **Enforcement:** The system checks the `can_message` edge in SurrealDB. If valid, the message is routed; otherwise, "Permission Denied".

#### 3. Genesis Implementation
We will build the `RecruitmentSquad` using Agno agents.
*   **AgentCreator:** Generates system prompts for new agents based on user requirements.
*   **ToolCreator:** Searches the tool library (or writes new code via `CodingSquad`) to equip the new agents.
*   **SquadAssembler:** Writes the new configuration to SurrealDB and spins up the squad.

### Implementation Steps

1.  **Schema Design:** Finalize the SurrealDB schema for Agents, Squads, and Communication permissions.
2.  **Tool Standardization:** Adopt the `BaseTool` pattern (Pydantic models) for all internal tools.
3.  **Routing Layer:** Implement the "Switchboard" in the main application loop that routes messages between agents based on the defined hierarchy.

### Refined Workflow: "The Boardroom"
1.  **User:** "We need to launch a marketing campaign."
2.  **CMO (Chief Marketing Officer Agent):** Receives the goal.
3.  **CMO:** Checks available sub-agents. Sees `Copywriter` and `GraphicDesigner`.
4.  **CMO:** Calls `send_message(recipient="Copywriter", content="Draft 3 tweet variations.")`.
5.  **Copywriter:** Executes and replies.
6.  **CMO:** Reviews. Calls `send_message(recipient="GraphicDesigner", content="Create images for these tweets.")`.
7.  **CMO:** Compiles final package and reports to User.
