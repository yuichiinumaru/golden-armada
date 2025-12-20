# Troubleshooting

Common issues and solutions for CodeSwarm.

## Configuration Errors

### `google.generativeai.types.generation_types.StopCandidateException` or API Errors
*   **Cause**: Invalid API key or quota exceeded.
*   **Solution**: Check your `GEMINI_API_KEY` in `.env`. Verify your billing status on Google AI Studio.

### `FileNotFoundError: .env`
*   **Cause**: The `.env` file is missing.
*   **Solution**: Create it in the root directory. See [Getting Started](./01-getting-started.md).

## Execution Errors

### `Access denied: ... is outside the project directory`
*   **Cause**: An agent tried to read/write a file outside the `target_project_path`.
*   **Solution**: The system sandbox (`codeswarm/tools.py`) prevents this. If valid, check your `--path` argument.

### `subprocess.TimeoutExpired`
*   **Cause**: `DevAgent` ran a script that took longer than 10 seconds.
*   **Solution**: Code execution is limited to 10 seconds (`codeswarm/tools.py`). Instruct the agent to write more efficient code or increase the timeout in `tools.py` (Developer modification required).

### `ModuleNotFoundError`
*   **Cause**: Running the script from the wrong directory.
*   **Solution**: Always run from the repo root: `python -m codeswarm.main`.

## Debugging

### Viewing Logs
*   The system logs to the console and `codeswarm.log` (if configured in `logger.py`).
*   **Tip**: Look for `[DevAgent_X]` or `[RevisorAgent_X]` tags to trace specific agent actions.

### State Recovery
*   If the system crashes, check `generated_code/codeswarm_state.json`.
*   **Restoration**: The system automatically attempts to load this file on the next run. To start fresh, delete this file.
