# CodeSwarm Project Analysis and Problems Report

## 1. Project Overview
CodeSwarm is a multi-agent coding system orchestrated by the Agno framework, migrated from Google ADK. It involves Admin, Developer, and Revisor agents working in rounds to achieve a project goal.

## 2. Identified Problems

### 2.1. Codebase vs. Documentation Discrepancies
-   **Missing `AGENTS.md`**: The `AGENTS.md` file is referenced as a place for agent instructions but does not exist in the root or `docs/`.
-   **Missing Prompts KB Documentation**: `README.md` and `docs/tasklist.md` mention `codeswarm/prompts/kb/` but do not explain its usage. The files in `codeswarm/prompts/kb/` are not currently used by the agents.
-   **Legacy Code References**: Some comments and file names (e.g., in `tests/`) still reference ADK concepts or legacy paths.
-   **Tool Discrepancies**:
    -   `execute_python_code` and `execute_shell_command` are defined in `codeswarm/tools.py` but are **not assigned to any agent** in `codeswarm/agents.py`. The DevAgent currently cannot run the code it writes.
    -   `RevisorAgent` has `read_file` but relies on the orchestration layer to pass the `file_to_edit_or_create` path.

### 2.2. Architectural and Logic Issues
-   **AgentOS Logic**:
    -   **One-Shot Revisor**: If the Revisor rejects a task, the `_run_single_task` function returns the rejection, and the orchestration loop marks it as `REJECTED` or `IN_PROGRESS` (logic seems to map rejection to `REJECTED`). There is **no immediate feedback loop** where the DevAgent tries to fix the code within the same round. The task is effectively dropped or has to be re-planned in the next round, but the `_planning_phase` logic does not explicitly handle re-assigning rejected tasks.
    -   **State Persistence**: `codeswarm_state.json` is not persisted to disk. State is held in memory (`self.session_state`). If the script crashes, progress is lost.
    -   **Parallel Execution**: Uses `concurrent.futures`. While efficient, debugging parallel agent execution can be hard. The logging inside `_run_single_task` uses `print`, which might get interleaved.

### 2.3. Agent Configuration
-   **DevAgent Capabilities**: DevAgent lacks the ability to execute code, which limits its ability to self-verify before sending to Revisor.
-   **Prompt/Schema Mismatch**:
    -   `DevAgent` prompt expects `dev_id` in input, but `_run_single_task` passes it. This is consistent, but worth verifying.
    -   `AdminAgent` output schema `AdminTaskOutput` expects a list of `TaskAssignment`. The `agent_os.py` logic correctly handles this, but the prompt needs to ensure the Admin actually produces this structure reliably.

### 2.4. Testing
-   **Test Coverage**: `tests/` contains async tests for agents, but they rely on mocks or live API calls (which might fail without keys/environment).
-   **Integration Tests**: There is `tests/test_flow_mock.py` which mocks the flow. A real end-to-end test with a simple goal (e.g. "print hello world") is needed to verify the Agno integration with live models.

### 2.5. Knowledge Base (KB) Usage
-   The files in `codeswarm/prompts/kb/` (e.g., `Problem Solving Framework.json`) are present but **not loaded or injected** into the agent instructions in `codeswarm/agents.py`. This means the "Advanced Research" phase tasks regarding KB integration are unfinished.

## 3. Unfinished Tasks (from Tasklist & Analysis)
-   [ ] **Integrate KB Files**: Load relevant KB JSONs from `codeswarm/prompts/kb/` into agent instructions.
-   [ ] **Enable Code Execution for DevAgent**: Add `execute_python_code` (and potentially shell) to DevAgent's toolset and update prompt to encourage self-correction.
-   [ ] **Implement Feedback Loop**: Modify `_run_single_task` to allow DevAgent to retry if Revisor rejects, up to a limit (e.g., 3 attempts).
-   [ ] **Persist State**: Save `session_state` to `codeswarm_state.json` after every round or phase.
-   [ ] **Verify Live Execution**: Run a live test with Gemini API.
-   [ ] **MCP Integration**: Evaluate and implement MCP tools (as suggested in `ideas.md`).

## 4. Recommendations
1.  **Immediate Fix**: Add `execute_python_code` to DevAgent.
2.  **Immediate Fix**: Implement a basic feedback loop in `_run_single_task`.
3.  **Documentation**: Create `AGENTS.md` and update `README.md`.
4.  **Feature**: Load KBs into agents.
