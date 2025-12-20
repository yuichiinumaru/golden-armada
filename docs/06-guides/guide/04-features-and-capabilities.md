# Features and Capabilities

CodeSwarm includes several advanced features to enhance code quality and autonomy.

## 1. Dev-Revisor Feedback Loop

Unlike simple "fire-and-forget" coding agents, CodeSwarm implements a strict verification loop.

*   **Logic**: Located in `codeswarm/agent_os.py` (`_run_single_task`).
*   **Process**:
    1.  **DevAgent** attempts the task.
    2.  **RevisorAgent** reviews the output.
    3.  **If Rejected**: The Revisor's feedback is fed back into the DevAgent's input as `previous_feedback`.
    4.  **Retry**: The DevAgent tries again.
    5.  **Limit**: This repeats up to 3 times per task.

## 2. Context-Aware Knowledge Retrieval

Before a developer starts working, the system fetches relevant context.

*   **Agent**: `KnowledgeAgent` (`codeswarm/agents.py`).
*   **Workflow**:
    *   The `AgentOS` constructs a query based on the task description and target file.
    *   The `KnowledgeAgent` searches existing files and imports to provide a "Context Snippet".
    *   This snippet is injected into the DevAgent's prompt, reducing hallucinations and ensuring consistency with existing code.

## 3. Parallel Task Execution

CodeSwarm executes tasks concurrently to speed up development.

*   **Implementation**: Uses `concurrent.futures.ThreadPoolExecutor` in `codeswarm/agent_os.py`.
*   **Configuration**: The number of concurrent threads is controlled by the `--pairs` argument (or `DEFAULT_PAIRS` in config).
*   **Safety**: Each task operates on a specific file, minimizing merge conflicts (though file locking is not currently implemented).

## 4. Strategic Planning

The system doesn't just execute tasks blindly; it plans strategically.

*   **Agent**: `PlannerAgent`.
*   **Phase**: `_strategic_planning_phase`.
*   **Output**: Updates a `todo.md` file (or equivalent plan in state) at the start of every round, allowing the system to adapt to new discoveries or changes in scope.

## 5. Tool-Use & Code Execution

DevAgents are equipped with a Python execution environment.

*   **Tool**: `execute_python_code` (`codeswarm/tools.py`).
*   **Capability**: The agent can write a script, run it to verify the output, and then refine it—all before submitting it to the Revisor.
