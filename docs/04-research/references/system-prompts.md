# System Prompts: The DNA of AI Agents

## Synthesis
The `x1xhlol-system-prompts` repository is a massive collection of "leaked" or open-sourced system prompts from the world's leading AI engineering tools: **Cursor, Devin, Windsurf, Replit Agent, v0, and more.**

This is not just a list of instructions; it is a masterclass in **Agentic Engineering**. By analyzing these prompts, we can reverse-engineer the "thought processes" that make these tools so effective.

**Key Archetypes Discovered:**

1.  **The "Senior Pair Programmer" (Cursor/Windsurf):**
    *   **Philosophy:** "I am an expert, but I listen to you."
    *   **Mechanism:** Heavy emphasis on *context gathering* first (`grep_search`, `read_file`) before making changes.
    *   **Constraint:** "NEVER output code to the USER, unless requested. Instead use one of the code edit tools." (This prevents hallucinated code that isn't actually applied).
    *   **Memory:** Explicit "Memory Rating" prompts to decide what to persist long-term.

2.  **The "Autonomous Engineer" (Devin):**
    *   **Philosophy:** "I am a real software engineer using a real computer."
    *   **Mechanism:** Explicit "Planning" mode vs "Standard" mode. Uses a `<think>` tag for internal monologue before taking action.
    *   **Tooling:** Has access to a browser, shell, and editor. It handles environment issues by reporting them but trying to work around them.

3.  **The "UI Generator" (v0):**
    *   **Philosophy:** "I am v0, Vercel's AI-powered assistant."
    *   **Mechanism:** strict adherence to MDX and React component structures (`<CodeProject>`). It "knows" the environment (Next.js, Tailwind, Shadcn) implicitly.

## Strategic Ideas for Golden Armada
We can lift the best "mental models" from these prompts to upgrade our Agno agents.

1.  **The `<think>` Tag Pattern (Devin):**
    *   We should instruct our generic `Worker` agents to output a `<think>` block *before* calling any tools.
    *   *Prompt:* "Before taking action, write a `<think>` block reflecting on what you know, what you need to find out, and your plan."
    *   *Benefit:* Reduces impulsive tool calling and improves reasoning chain visibility.

2.  **The "Memory Rater" (Cursor):**
    *   Instead of blindly saving everything, we need a specific "Critic" agent (or just a prompting step) that evaluates a piece of information: "Is this a general rule (score 5) or a one-off detail (score 1)?"
    *   *Implementation:* A `MemoryFilter` agent that sits between the `Chat` loop and the `SurrealDB` memory store.

3.  **Context-First Mandate (Windsurf/Cursor):**
    *   Agents often try to edit files they haven't read. We must enforce a rule: "You are forbidden from calling `edit_file` on a file you have not called `read_file` on in this turn."
    *   *Mechanism:* We can enforce this in the Agno `Agent` logic or simply via a strong System Prompt.

4.  **"Planning" vs "Execution" Modes (Devin):**
    *   We should explicitly model these states in our `SquadLeader`.
    *   *Plan Mode:* Read-only tools + Search. Output = `Plan` object.
    *   *Execute Mode:* Edit tools + Run. Output = `Result` object.

## Integration Plan (Agno + SurrealDB + Gemini 3)

### 1. The "Golden System Prompt"
We will create a master system prompt builder in Python that composes the best parts of these references.

```python
SYSTEM_PROMPT_TEMPLATE = """
You are a Golden Armada Agent.
{role_description}

<core_philosophy>
1. **Context First:** Never act on assumptions. Search and Read before you Edit.
2. **Think:** Always output a <think>...</think> block before your final answer or tool call.
3. **Atomic Edits:** When editing code, do not output the whole file. Use the `apply_diff` tool.
</core_philosophy>

<memory_protocol>
Check your `long_term_memory` tool for previous learnings.
If you learn a new general rule/preference, call `save_memory`.
</memory_protocol>
"""
```

### 2. The "Prompt Engineer Squad"
This analysis validates the need for a dedicated squad that *optimizes* these prompts.
*   **Role:** Auto-tunes the system prompts based on task success/failure rates.
*   **Mechanism:** Uses `SPO` (from previous research) to rewrite the `SYSTEM_PROMPT_TEMPLATE` for specific agents.

### 3. Implementing the "Thinking" Tool
We don't need a tool for thinking, but we can treat the `<think>` block as a "virtual tool" that the UI renders differently (e.g., collapsed by default), similar to how DeepSeek R1 works.

### 4. V0-style UI Generation
For our `FrontendSquad`, we will copy v0's strict constraints: "You are working in a Next.js App Router environment. Use Tailwind. Use Lucide React." avoiding the "framework fatigue" where agents hallucinate random libraries.
