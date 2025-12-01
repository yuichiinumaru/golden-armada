# CodeSwarm Agno

This is a conversion of the CodeSwarm project to use the [Agno](https://agno.com) framework (formerly Phidata).

## Prerequisites

1.  Python 3.10+
2.  Install dependencies:
    ```bash
    pip install agno google-genai python-dotenv beautifulsoup4 requests
    ```
3.  Ensure `.env` file is present in the root directory with `GEMINI_API_KEY` (or `GOOGLE_API_KEY`).

## Structure

-   `codeswarm_agno/main.py`: The orchestrator script.
-   `codeswarm_agno/agents.py`: Agent definitions (Admin, Dev, Revisor, AdminLogger).
-   `codeswarm_agno/tools.py`: Tool definitions.
-   `codeswarm_agno/models.py`: Pydantic models for structured output.
-   `codeswarm_agno/config.py`: Configuration loading.

## Running

Run the main module from the project root:

```bash
python -m codeswarm_agno.main --goal "Your project goal" --path "your_project_path" --rounds 1
```

## Changes from Original ADK Version

-   Replaced `google-adk` Agents with `agno.agent.Agent`.
-   Replaced ADK Workflow with a custom Python orchestration loop in `main.py`.
-   Tools are defined as standalone functions and passed to Agno agents.
-   Prompts are loaded from the existing JSON files and formatted for Agno.
-   Structured Output is handled using Pydantic models via `output_schema`.
