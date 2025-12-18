# Strategic Architecture: ARTEMIS Integration

## 1. Architecture Pattern
We will adopt a **Hexagonal Architecture (Ports & Adapters)** approach to integrate ARTEMIS concepts into CodeSwarm's CFA.

### Layers
*   **Layer 1 (Domain):** `PromptBuilder`, `AgentRegistry`.
*   **Layer 2 (Application):** `SpawnerService` (Orchestration).
*   **Layer 3 (Infrastructure):** `ThreadPoolAdapter` (Current), `DockerAdapter` (Future), `JinjaPromptAdapter`.

## 2. Domain Decomposition

### Domain: DynamicPrompting
*   **Responsibility:** Constructing the "perfect" system prompt for a specific task at runtime.
*   **Entities:**
    *   `PromptContext`: Data class holding current task, phase, and constraints.
    *   `SkillModule`: A reusable prompt segment (e.g., "Python Expert", "Security Auditor").
    *   `PromptBuilder`: Service that combines Modules + Context -> String.

### Domain: AgentLifecycle (The Spawner)
*   **Responsibility:** Managing the creation, execution, and teardown of agents.
*   **Entities:**
    *   `AgentSpec`: Configuration for an agent (Role, Tools, Memory access).
    *   `AgentHandle`: A reference to a running/queued agent.
    *   `Spawner`: Interface `spawn(spec) -> AgentHandle`.

## 3. Technology Decisions (ADRs)

### ADR 001: Spawner Abstraction
*   **Decision:** We will create a `Spawner` abstract base class. The initial implementation `ThreadSpawner` will wrap the existing `ThreadPoolExecutor`.
*   **Rationale:** This allows us to adopt the ARTEMIS "Spawner" pattern immediately without rewriting the entire async engine. It paves the way for a future `ProcessSpawner` or `RemoteSpawner` (Rust) without changing business logic.

### ADR 002: Compositional Prompting
*   **Decision:** We will strictly forbid hardcoded system prompts in `agents.py`. All prompts must be generated via `PromptBuilder`.
*   **Rationale:** To achieve ARTEMIS-level adaptability. Hardcoded prompts are brittle and fail to adapt to changing "Rounds" or "Goals".

## 4. Data Flow (Spawner)
1.  `AgentOS` (Orchestrator) determines need for a "Dev" task.
2.  `AgentOS` creates `AgentSpec(role="Dev", capabilities=["Read", "Write"])`.
3.  `AgentOS` calls `Spawner.spawn(spec)`.
4.  `Spawner` (ThreadImpl) instantiates the Agent, injects the built Prompt, and submits to thread pool.
5.  `Spawner` returns `AgentHandle` (Future wrapper).
