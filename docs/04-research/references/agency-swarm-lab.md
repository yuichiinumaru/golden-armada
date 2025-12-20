# Agency Swarm Lab Analysis

## 1. Synthesis: The Agency Swarm Lab
The `agency-swarm-lab` repository serves as a testing ground and showcase for the **Agency Swarm** framework. It contains a collection of distinct, purpose-built agencies that demonstrate different architectural patterns, tool integrations, and agent interaction models. Unlike a single monolithic application, this repo provides "recipes" for specialized agent teams.

### Key Agencies & Capabilities:
1.  **WebDevCrafters**: A specialized team for frontend development (Next.js + MUI).
    *   **Designer Agent**: Uses Playwright/Selenium to take screenshots of the running app (`localhost:3000`) and analyzes them using GPT-4V to provide visual feedback.
    *   **WebDeveloper Agent**: Uses advanced file manipulation tools and a **React Component Injector** (parsing JSX to JSON and back) to modify code structurally rather than just regex/string replacement.
    *   **CEO**: Orchestrates the flow between design and code.
2.  **CodeSolutionAgency**: A general-purpose coding squad.
    *   **Planner Agent**: Enforces a "Plan First" workflow using a `CreatePlan` tool to break down tasks into steps (Devid vs Browsing).
    *   **Devid (Developer)**: Standard filesystem and command execution agent.
    *   **Browsing Agent**: Research and documentation retrieval.
3.  **MetaMarkAgency**: A marketing automation squad.
    *   **FacebookManagerAgent**: Manages campaigns, ad sets, and posts via the Facebook Marketing API.
    *   **AdCopy & ImageCreator Agents**: Generates copy and DALL-E 3 images tailored to specific audiences.
4.  **AIProjectManager**: A productivity integration squad.
    *   Connects **Slack** events to **Notion** databases.
    *   Demonstrates event-driven agent triggers (Slack mentions) vs. just chat-driven.
5.  **OpenSourceSwarm / AstraOpenSourceSwarm**:
    *   Demonstrates running agencies with **local models (Ollama)** or non-OpenAI providers (Anthropic, Gemini) using `litellm`.

## 2. Strategic & Architectural Ideas for Golden Armada

### A. The Visual Feedback Loop (Critical for Frontend)
The `WebDevCrafters` agency implements a pattern missing in many text-based coding agents: **Visual Grounding**.
*   **Mechanism**: The `Designer` agent doesn't just "imagine" the UI; it spins up a headless browser, screenshots the actual build, and critiques the pixels.
*   **Benefit**: This closes the loop on CSS/Layout bugs that LLMs often hallucinate fixes for.
*   **Relevance**: The Golden Armada's "Frontend Squad" must possess this visual verification capability to be effective.

### B. Structural Code Manipulation (AST over Regex)
The `WebDeveloper` agent in `WebDevCrafters` uses a `ComponentInjectorTool` that:
1.  Parses React/JSX code into a JSON tree (AST-like structure) using `react-serialize`.
2.  Injects new components at specific indices in the JSON tree.
3.  Renders the JSON back to JSX.
*   **Insight**: This is significantly more robust than LLMs trying to "replace lines 10-15" which often fails due to indentation or context mismatches.
*   **Relevance**: Golden Armada should prioritize AST-based tools for code modification where possible.

### C. The "Planner" Pattern
The `CodeSolutionAgency` explicitly separates **Planning** from **Execution**.
*   **Mechanism**: The `PlannerAgent` uses a `CreatePlan` tool that generates a structured list of steps. The `Devid` agent simply executes the current step.
*   **Benefit**: Prevents the "Rabbit Hole" effect where a coding agent gets lost in debugging a minor error and loses sight of the overall feature.

### D. Model Agnosticism via LiteLLM
The `OpenSourceSwarm` examples show how to decouple the *Agent Framework* from the *LLM Provider*.
*   **Strategy**: Using a proxy (LiteLLM) allows the Agency to switch between GPT-4o, Claude 3.5 Sonnet, or Llama 3 without changing the agent code.

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

To integrate these high-value patterns into the Golden Armada while maintaining our specific stack:

### Step 1: The "Visual QA" MCP Service
Instead of embedding browser code directly into an agent (as in `agency.py`), we will wrap the Visual Feedback capability into a dedicated MCP Server.
*   **Tool**: `verify_frontend_visuals(url: str, requirements: str) -> Analysis`
*   **Implementation**: A Dockerized MCP server running Playwright. It returns a screenshot + Gemini 1.5 Pro analysis of the screenshot against the requirements.
*   **Integration**: The `FrontendSquad` will have access to this MCP tool.

### Step 2: AST-Based Code Tools
We will port the logic from `ComponentInjectorTool` (currently Node.js scripts wrapped in Python) into a proper **Language Server Protocol (LSP)** or **AST-MCP** service.
*   **Refinement**: Instead of ad-hoc scripts, use a standardized AST parser (e.g., `tree-sitter`) exposed via MCP to allow agents to "Insert function X into Class Y" reliably.

### Step 3: SurrealDB as the "Plan State"
The `CodeSolutionAgency` stores plans in memory. Golden Armada will store them in SurrealDB.
*   **Schema**:
    ```sql
    DEFINE TABLE plan SCHEMAFULL;
    DEFINE FIELD steps ON TABLE plan TYPE array;
    DEFINE FIELD current_step ON TABLE plan TYPE int;
    DEFINE FIELD status ON TABLE plan TYPE string;
    ```
*   **Workflow**: The `Planner` agent creates a `plan` record. The `Executor` agents query the active plan, execute the `current_step`, and update the record. This allows long-running, asynchronous execution that survives restarts.

### Step 4: "Squad Recipes" in Genesis
We will treat the `agency-swarm-lab` folders as templates for our **Genesis Agency**.
*   **Concept**: When a user asks Genesis for "a team to manage my Facebook Ads", Genesis looks up the "Marketing Squad" recipe (inspired by `MetaMarkAgency`) and spawns those specific agents (AdCopy, ImageGen, FBManager) connected via the Armada Gateway.

### Step 5: Event-Driven Triggers (Slack/Webhooks)
Inspired by `AIProjectManager`, we will implement an **Event Bus** in the Golden Armada.
*   **Architecture**: An API Gateway (FastAPI) receives webhooks (Slack, GitHub, Stripe). These events are pushed to SurrealDB. A `DispatcherAgent` watches the DB and wakes up the relevant Squad (e.g., "Project Manager Squad") to handle the event.

### Summary
The `agency-swarm-lab` provides the **tactical implementation details** (specific tools, prompts, and flows) that fill in the **strategic architecture** of the Golden Armada. We will "upgrade" these ideas from local, ephemeral scripts to persistent, database-backed, distributed services.
