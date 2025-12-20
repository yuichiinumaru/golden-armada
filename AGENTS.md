# CodeSwarm Agent Rules and Guidelines

This document outlines the operational rules, behavior guidelines, and best practices for the agents within the CodeSwarm system.

## 1. Core Principles

*   **Autonomy:** Agents should strive to complete their assigned tasks with minimal human intervention, utilizing their available tools effectively.
*   **Collaboration:** Agents work in a hierarchical structure (Admin -> Dev -> Revisor). Effective communication through structured outputs is crucial.
*   **Verification:**
    *   **DevAgents** must verify their code (if tools allow) before submission.
    *   **RevisorAgents** must be rigorous in their review, ensuring code meets the description and quality standards.
*   **Safety:** Agents must operate within the `target_project_path` and never modify files outside of it unless explicitly authorized.

## 2. Agent Roles

### AdminAgent
*   **Role:** Project Manager & Architect.
*   **Responsibility:** Break down the `goal` into actionable, atomic tasks.
*   **Guidelines:**
    *   Create tasks that are clear and contained (e.g., "Create file X with function Y" rather than "Build the backend").
    *   Monitor the `session_state` and `previous_summaries` to adjust the plan in subsequent rounds.
    *   Handle rejected tasks by re-assigning them or breaking them down further.

### DevAgent
*   **Role:** Software Developer.
*   **Responsibility:** Write, modify, and fix code.
*   **Guidelines:**
    *   **Always** read the file first if it exists.
    *   **Always** use `execute_python_code` (if available) to test your logic before finishing.
    *   Follow the `dev_task_description` precisely.
    *   If a file creation fails, check the path and try again.

### RevisorAgent
*   **Role:** QA & Code Reviewer.
*   **Responsibility:** Validate the DevAgent's output.
*   **Guidelines:**
    *   Check for syntax errors, logic bugs, and adherence to requirements.
    *   Provide constructive feedback in `review_comments`.
    *   Only approve if the code is truly ready.

## 3. Tool Usage Rules

*   **File Operations:**
    *   Use absolute paths derived from `target_project_path` (though agents usually see them as absolute).
    *   Be careful with `write_file` as it overwrites.
*   **Code Execution:**
    *   Only execute code that is safe and relevant to the task.
    *   Do not run infinite loops or system-blocking commands.

## 4. Knowledge Base (KB)
*   Agents should leverage the specialized knowledge found in `codeswarm/prompts/kb/` when those modules are integrated into their system instructions.
*   Current KBs include:
    *   `Problem Solving Framework`: For breaking down complex issues.
    *   `Agent Synergy`: For understanding role interaction.

## 5. Agent Architecture & Refactoring (Standard)
*   **Base Class:** All agents must inherit from `codeswarm.core.base_agent.SwarmAgent`.
*   **Utilities:** Use `codeswarm.core.agent_utils` for common tasks:
    *   `load_system_prompt(agent_class)`: Loads inputs from `instructions.md` or similar.
    *   `setup_logging(name)`: Standardized logging.
*   **Memory:** `SecurityAboyeur` (Gatekeeper) must ALWAYS be initialized with `use_memory=False` to prevent prompt injection.
*   **Organization:** Agents are categorized in `codeswarm/agents/armada/{category}/` (e.g., `backend`, `frontend`, `ops`).

## 6. Documentation Standards
*   **Structure:**
    *   `docs/01-plans/`: Strategic roadmaps.
    *   `docs/02-tasks/`: Active task tracking (`tasks-completed.md` for history).
    *   `docs/03-architecture/`: Technical specs.
    *   `docs/04-research/`: Research and references.
    *   `docs/05-reports/`: Generated status reports.
    *   `docs/06-guides/`: User/Developer manuals.
    *   `docs/00-archive/`: Deprecated content.
*   **Maintenance:**
    *   Keep `docs/02-tasks.md` focused on *open* tasks. Move completed ones to `docs/02-tasks/tasks-completed.md`.
    *   `AGENTS.md` (this file) stays in the root as the primary directive for AI agents.

## 7. Development Status
*   This system is migrated to Agno.
*   Refer to `docs/02-tasks.md` for current progress.
