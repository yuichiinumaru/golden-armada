# RFC 001: Integration of PewPewCLI Concepts

## Objective
Enhance `CodeSwarm`'s CLI capabilities to allow human operators to interact with the agent's task queue (`TaskTree`) efficiently, inspired by `pew-pew-cli`. This enables dynamic task injection (e.g., pasting a bug report) and status checks without manually editing JSON/Markdown files.

## Proposed Changes

### 1. New CLI Service
Create `codeswarm/services/cli_service.py` to handle CLI-specific logic, decoupling it from `main.py`.

### 2. New Commands
Extend `codeswarm/main.py` (using `argparse` or migrating to `typer`/`click`) to support:
*   `paste --target tasks`: Reads from system clipboard and adds a new task to the `TaskTree` (via `AdminAgent` or direct injection).
*   `next task`: Displays the current `IN_PROGRESS` task and the next `PENDING` task.
*   `reset tasks`: Resets task statuses (useful for debugging).

### 3. Dependencies
*   Add `pyperclip` to `requirements.txt` for clipboard access.

## Implementation Steps (Checklist)

1.  [ ] **Setup:** Add `pyperclip` to `requirements.txt`.
2.  [ ] **Architecture:** Create `CliService` class in `codeswarm/services/cli_service.py`.
    *   Implement `add_task_from_clipboard()`.
    *   Implement `get_next_task()`.
3.  [ ] **Porting:** Adapt logic from `pew-pew-cli`'s `handlePasteTasks` (TypeScript) to Python.
    *   *Source:* `references/pew-pew-cli/src/core/cli.service.ts`
    *   *Target:* `codeswarm/services/cli_service.py`
4.  [ ] **Integration:** Update `codeswarm/main.py` to add arguments/subparsers for these commands.
5.  [ ] **Verify:** Test `python -m codeswarm.main next task` output.
