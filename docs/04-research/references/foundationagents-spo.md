# Foundation Agents SPO (Self-Supervised Prompt Optimization) Analysis

## 1. Synthesis: What is SPO?
The `foundationagents-spo` repository implements **Self-Supervised Prompt Optimization**, a framework for automatically refining Large Language Model (LLM) prompts without requiring large labeled datasets or human feedback loops.

### Core Methodology
1.  **Iterative Hill-Climbing**: It treats prompt engineering as an optimization problem. It starts with a base prompt and iteratively modifies it to maximize a specific objective.
2.  **LLM-as-a-Judge**: Instead of relying on ground truth (which is expensive) or simple metrics (which are noisy), it uses a separate, high-quality LLM instance (the "Evaluator") to compare the outputs of two different prompts (A vs. B) and decide which one better meets the defined `requirements`.
3.  **Roles**:
    *   **Optimizer**: Generates a new, improved prompt based on the previous best prompt and an analysis of why it failed or succeeded.
    *   **Executor**: Runs the prompt against a set of test cases (QA pairs).
    *   **Evaluator**: Blindly compares the `Executor`'s output for the new prompt vs. the old prompt to determine the winner.

### Key Components
*   **Templates (YAML)**: Configuration files defining the initial `prompt`, `requirements`, and few-shot `qa` examples.
*   **`PromptOptimizer`**: The central controller that manages the optimization rounds, directory state (`round_1`, `round_2`), and invokes the LLM client.
*   **`QuickEvaluate`**: Implements the comparison logic, notably handling **position bias** by randomly swapping A/B choices presented to the judge.

## 2. Strategic & Architectural Ideas for Golden Armada

### A. The "Trainer Squad" Concept
The Golden Armada is built on specialized Squads. SPO suggests a meta-pattern: a **Trainer Squad** whose sole purpose is to optimize the system prompts of *other* squads before they are deployed or when they underperform.
*   **Idea**: When a user creates a new "Market Analysis Squad", the Trainer Squad generates 10 synthetic test cases, runs SPO for 5 rounds, and delivers a highly tuned system prompt, rather than a raw zero-shot prompt.

### B. Automated Regression Testing via LLM-Judge
The `QuickEvaluate` logic (blind A/B testing) is a powerful pattern for **Continuous Integration (CI)** for Agents.
*   **Idea**: Whenever we upgrade the Golden Armada's underlying model (e.g., GPT-4o to Gemini 1.5 Pro) or modify a core tool, we run an "Evaluation" pass. If the Judge deems the new outputs worse than the baseline, the deployment is halted.

### C. Prompt Versioning & Lineage
SPO uses a file-based system (`round_1`, `round_2`) to track prompt evolution.
*   **Idea**: Golden Armada should store prompt versions in **SurrealDB**. This allows us to "rollback" an agent's personality or instructions if an optimization leads to a local maximum that is actually worse in edge cases.

### D. Synthetic Few-Shot Generation
SPO relies on a small set of QA pairs.
*   **Idea**: We can use a "Data Generator Agent" to create these QA pairs from the user's high-level requirements, making the optimization process completely autonomous (User Requirement -> Synthetic Data -> Optimized Prompt).

## 3. Integration Plan: Agno + SurrealDB + Gemini 3

To integrate SPO's capabilities into the Golden Armada stack:

### Step 1: `PromptOptimizationService` (MCP Server)
Encapsulate the SPO logic into a dedicated **MCP Server**.
*   **Tool**: `optimize_agent_prompt(current_instruction: str, requirements: str, test_cases: List[Dict]) -> str`
*   **Logic**:
    1.  Accepts a draft instruction.
    2.  Runs the internal loop (Optimize -> Execute -> Evaluate) using Agno agents as the workers.
    3.  Returns the optimized instruction string.

### Step 2: SurrealDB Schema for Prompt Engineering
Store the optimization lifecycle in the graph.
```sql
DEFINE TABLE prompt_version SCHEMAFULL;
DEFINE FIELD instruction ON TABLE prompt_version TYPE string;
DEFINE FIELD score ON TABLE prompt_version TYPE float;
DEFINE FIELD parent ON TABLE prompt_version TYPE record<prompt_version>;
DEFINE FIELD created_at ON TABLE prompt_version TYPE datetime DEFAULT time::now();

DEFINE TABLE optimization_run SCHEMAFULL;
DEFINE REL runs_on ON TABLE optimization_run TYPE record<prompt_version>; -- Edge to the prompt being optimized
```

### Step 3: The "Judge" Agent Pattern
Implement a standard `JudgeAgent` in Agno that uses the `QuickEvaluate` strategy.
*   **System Prompt**: "You are an impartial judge. You will be given two responses to a query. Compare them based on the following requirements: {requirements}. Output ONLY 'A' or 'B'."
*   **Usage**: Used by the `PromptOptimizationService` and potentially by the `QualityAssuranceSquad`.

### Step 4: Genesis Agency Workflow Update
Update the **Genesis Agency** (responsible for spawning new squads) to include an optional "Optimization Phase".
*   **Flow**:
    1.  User: "Create a squad to write Python scripts for finance."
    2.  Genesis: Drafts initial prompt.
    3.  Genesis: Generates 3 test cases ("Write a script to calculate RSI...", etc.).
    4.  Genesis -> `PromptOptimizationService`: "Optimize this prompt against these cases."
    5.  Service: Returns optimized prompt.
    6.  Genesis: Deploys final squad.

### Summary
SPO provides the **algorithm** for self-improving agents. By integrating this into the Golden Armada's infrastructure (MCP + SurrealDB), we move from static, hand-crafted prompts to **dynamic, self-evolving agent instructions**, significantly increasing reliability and performance without constant human tweaking.
