# Reference Analysis: Self-Supervised Prompt Optimization (SPO)

**Source:** `gitingest-foundationagents-spo.txt`
**Repo:** FoundationAgents/SPO (inferred)
**Date:** 2025-03-31

---

## 1. Synthesis: What is SPO?

SPO (Self-Supervised Prompt Optimization) is an automated framework designed to refine and optimize Large Language Model (LLM) prompts without requiring large labeled datasets or human intervention. It leverages the "LLM-as-a-Judge" paradigm to create a closed-loop optimization cycle.

### Core Philosophy
The central premise of SPO is that LLMs can critique and improve their own instructions if provided with:
1.  **A Base Prompt**: The starting instruction.
2.  **Requirements**: Specific constraints or goals (e.g., "be concise," "return JSON").
3.  **Few-Shot Examples (QA Pairs)**: A small set of inputs and expected outputs (or "golden answers").
4.  **Optimization Loop**: An iterative process where the model generates new prompts, tests them, evaluates the results, and selects the best performer.

### Key Components

#### 1. The Optimizer Loop (`components/optimizer.py`)
This is the engine of the system. It orchestrates the following cycle:
*   **Generation**: Uses a meta-prompt (`PROMPT_OPTIMIZE_PROMPT`) to ask an LLM (the "Optimizer Model") to rewrite the current prompt based on previous failures or successful patterns.
*   **Execution**: Runs the new prompt against a set of test cases (QA pairs) using an "Execution Model".
*   **Evaluation**: Uses a third LLM role (the "Evaluator Model") to compare the new output against the "golden answer" or the specific requirements. It essentially performs A/B testing between the previous best prompt and the new candidate.
*   **Selection**: If the new prompt performs better (higher win rate in the pairwise comparison), it becomes the new baseline.

#### 2. The LLM Roles
SPO distinguishes between three distinct LLM roles, which can be filled by different models (e.g., GPT-4o for optimization/evaluation, GPT-4o-mini for execution to save costs):
*   **Optimizer**: The creative architect. It analyzes *why* a prompt failed and proposes a structural change (e.g., "Add a chain-of-thought requirement").
*   **Executor**: The subject. It performs the actual task using the candidate prompt.
*   **Evaluator**: The judge. It blindly compares outputs (A vs. B) to determine which better meets the criteria.

#### 3. Configuration & State
*   **YAML Templates**: Prompts and datasets are defined in YAML files (`settings/*.yaml`), making them portable and version-controllable.
*   **Workspace**: Results, history, and metrics are stored in a file-based workspace, tracking the evolution of the prompt over `k` rounds.

---

## 2. Strategic Ideas for CodeSwarm (Golden Armada)

The concepts in SPO are directly applicable to the "Golden Armada" vision, specifically for the **Self-Improvement** and **Quality Assurance** capabilities of the agents.

### A. The "Prompt Engineer" Squad
Instead of static prompts hardcoded into our agents, we can treat prompts as **dynamic assets** managed by a specialized Squad.
*   **Idea**: A `PromptRefinerAgent` whose sole job is to take a failing agent (e.g., a WebScraper that keeps missing data) and optimize its system prompt using recent logs as the "test set".
*   **Benefit**: Agents become anti-fragile. If an agent encounters a new edge case, the system can "train" a better prompt to handle it automatically.

### B. LLM-as-Judge Integration (The "Revisor" Role)
We already have a "Revisor" role in our `AGENTS.md` definition. SPO provides a concrete implementation pattern for this.
*   **Idea**: Formalize the Revisor's workflow using the SPO `QuickEvaluate` logic. The Revisor shouldn't just "look" at code; it should run it (where safe) or compare it against a "Golden Standard" using a rubric.
*   **Benefit**: Standardized, metric-driven quality control for all agent outputs.

### C. Evolutionary Memory
SPO keeps a history of "Best Rounds". We can map this to **SurrealDB**.
*   **Idea**: Store prompt versions in a Graph.
    *   `Nodes`: Prompt Versions.
    *   `Edges`: "Derived From" (with attributes like improvement reason).
    *   `Properties`: Performance scores, cost, latency.
*   **Benefit**: We build a "phylogenetic tree" of our agents' cognition. We can roll back to a previous "stable" personality if a new optimization causes regression.

### D. Test-Driven Agent Development (TDAD)
SPO relies on `qa` pairs (inputs/outputs). This aligns perfectly with TDD.
*   **Idea**: Every Agent in the Armada must have a `golden_dataset` stored in SurrealDB. Before an agent is deployed or updated, it must pass the "SPO Gauntlet" — its prompt is optimized until it achieves a threshold score on this dataset.

---

## 3. Integration Plan

We will integrate SPO's logic into the **Golden Armada** by creating a **Prompt Engineering Toolkit** and a **Testing/Evaluation Subsystem** within our Agno + SurrealDB stack.

### Phase 1: The `PromptOptimizer` Toolkit (Agno)

We will not import the SPO code directly but re-implement its core logic as an Agno `Toolkit`.

**File:** `codeswarm/agno-agents/toolkits/prompt_optimizer.py`

```python
from agno.tools import Toolkit
from agno.agent import Agent
from typing import List, Dict

class PromptOptimizerToolkit(Toolkit):
    def __init__(self, db_client):
        super().__init__(name="prompt_optimizer")
        self.db = db_client

    def register(self, agent: Agent):
        agent.add_tool(self.optimize_prompt)
        agent.add_tool(self.evaluate_candidate)

    def optimize_prompt(self, current_prompt: str, requirements: str, failures: List[Dict]) -> str:
        """
        Uses a meta-prompt to suggest improvements to 'current_prompt'
        based on the provided 'failures' (examples where the agent failed).
        """
        # Implementation of the 'Optimizer' role from SPO
        pass

    def evaluate_candidate(self, prompt_candidate: str, test_cases: List[Dict]) -> float:
        """
        Runs the 'prompt_candidate' against 'test_cases' and uses an
        LLM-as-Judge to score the results.
        Returns a success rate (0.0 to 1.0).
        """
        # Implementation of the 'Evaluator' and 'Executor' roles
        pass
```

### Phase 2: SurrealDB Schema for Prompt Management

We need to store the artifacts of the optimization process.

**Schema Definitions:**

```sql
-- The Prompts Table: Stores the actual text and metadata
DEFINE TABLE prompts SCHEMAFULL;
DEFINE FIELD agent_id ON TABLE prompts TYPE record<agents>;
DEFINE FIELD version ON TABLE prompts TYPE int;
DEFINE FIELD content ON TABLE prompts TYPE string;
DEFINE FIELD description ON TABLE prompts TYPE string; -- "Added COT for better math"
DEFINE FIELD created_at ON TABLE prompts TYPE datetime DEFAULT time::now();

-- The Test Cases Table: The "Golden Dataset" for each agent
DEFINE TABLE test_cases SCHEMAFULL;
DEFINE FIELD agent_id ON TABLE test_cases TYPE record<agents>;
DEFINE FIELD input ON TABLE test_cases TYPE string; -- or JSON
DEFINE FIELD expected_output ON TABLE test_cases TYPE string; -- or JSON
DEFINE FIELD criteria ON TABLE test_cases TYPE string; -- "Must return valid JSON"

-- The Evaluations Table: Linking Prompts to Test Results
DEFINE TABLE evaluations SCHEMAFULL;
DEFINE FIELD prompt_id ON TABLE evaluations TYPE record<prompts>;
DEFINE FIELD score ON TABLE evaluations TYPE float;
DEFINE FIELD details ON TABLE evaluations TYPE object; -- Detailed pass/fail per test case
DEFINE FIELD evaluator_model ON TABLE evaluations TYPE string;
```

### Phase 3: The `AgentTrainer` Agent

We will create a specialized agent that uses the Toolkit and DB to "train" other agents.

**Workflow:**
1.  **Trigger**: A user or system admin notices `DeepResearcher` is failing to parse certain PDFs.
2.  **Input**: The admin provides 3 examples of the failed PDFs and the expected output.
3.  **Action**:
    *   `AgentTrainer` saves these as `test_cases` in SurrealDB.
    *   It pulls the current `DeepResearcher` prompt.
    *   It enters the **Optimization Loop** (SPO logic):
        *   *Round 1*: Analyze failures -> Generate Prompt V2 -> Run Tests -> Score: 40%.
        *   *Round 2*: Analyze V2 failures -> Generate Prompt V3 -> Run Tests -> Score: 85%.
    *   It selects Prompt V3.
4.  **Deployment**: The `AgentTrainer` updates the `DeepResearcher` configuration (hot-swap or PR).

### Detailed Logic Breakdown (SPO Adaptation)

The core SPO loop needs to be adapted to our async, distributed nature.

**The Meta-Prompt (Refining the Optimizer):**
We will adapt the `PROMPT_OPTIMIZE_PROMPT` from SPO to be Gemini-3 friendly (our standard LLM).

```text
ROLE: Prompt Architect
TASK: You are refining the system instructions for an autonomous AI agent.

INPUTS:
1. Current System Prompt: "{current_prompt}"
2. Recent Failure Cases:
   {failures}
3. Optimization Goal: "{requirements}"

INSTRUCTIONS:
- Analyze why the Current Prompt failed on the Failure Cases.
- Was it ambiguous? Did it lack structure? Did it hallucinate?
- Propose a REVISED System Prompt that addresses these specific failures without regressing on general performance.
- Use Chain-of-Thought (COT) to explain your changes before outputting the prompt.
```

**The Evaluator Logic (The Judge):**
We will implement the `QuickEvaluate` pairwise comparison logic but enhance it with specific error detection (JSON validation, tool usage validation).

```python
async def evaluate_response(response, golden_answer, criteria):
    """
    1. Structural Check: Is it valid JSON? (if required)
    2. Semantic Check: Does it match the golden answer's intent?
    3. Constraint Check: Did it violate any negative constraints?
    """
    if criteria.requires_json and not is_valid_json(response):
        return 0.0, "Invalid JSON"

    # LLM Judge for semantic comparison
    judge_prompt = f"""
    Compare the ACTUAL OUTPUT with the EXPECTED OUTPUT based on CRITERIA.
    CRITERIA: {criteria}
    EXPECTED: {golden_answer}
    ACTUAL: {response}

    Return a score 0.0 to 1.0.
    """
    return await llm.generate(judge_prompt)
```

### Conclusion

Integrating SPO transforms our agents from static scripts into **evolving software entities**. By coupling the `PromptOptimizer` toolkit with SurrealDB's versioning, we create a system where agents essentially "unit test" and "refactor" themselves (their prompts) continuously.
