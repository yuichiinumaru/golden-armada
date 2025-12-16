# Developer Guide

This section is for contributors who wish to modify or extend the CodeSwarm system itself.

## Project Structure

```text
codeswarm/
├── agents.py       # Agent definitions and factory functions
├── agent_os.py     # Main orchestration logic (AgentOS class)
├── config.py       # Configuration loader
├── main.py         # Entry point (CLI)
├── models.py       # Pydantic models for agent outputs
├── structures.py   # Internal data structures (TaskNode, TaskTree)
├── tools.py        # Tool implementations (file ops, execution)
└── prompts/        # JSON prompt templates
    └── kb/         # Knowledge Base modules
```

## Adding a New Agent

To add a new agent (e.g., `SecurityAgent`):

1.  **Define a Prompt**: Create `codeswarm/prompts/security_prompt.json`.
2.  **Create a Factory Function**: In `codeswarm/agents.py`, add `get_security_agent()`.
3.  **Register**: Initialize it in `codeswarm/agent_os.py` within the `__init__` method.

## Adding a New Tool

Tools are defined in `codeswarm/tools.py` as standalone functions.

1.  **Implement**: Write the function (e.g., `def scan_vulnerabilities(path): ...`).
2.  **Return Dict**: Ensure it returns a dictionary with `status` and `result`/`message`.
3.  **Assign**: Add the function to the `tools` list in the relevant agent's factory function in `codeswarm/agents.py`.

## Modifying Prompts & Knowledge Base

*   **Prompts**: Located in `codeswarm/prompts/*.json`. These define the system instructions.
*   **Knowledge Base**: Located in `codeswarm/prompts/kb/*.json`. These are injected into prompts via `load_kb_content` in `codeswarm/agents.py`. Adding new reasoning modules here affects how agents "think".

## Running Tests

The project includes tests in the `tests/` directory.

*   **Run all tests**:
    ```bash
    python -m unittest discover tests
    ```
*   **Note**: Some tests may require API keys or mock environments.
