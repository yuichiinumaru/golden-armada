# CodeSwarm

CodeSwarm is a multi-agent coding system orchestrated by the [Agno](https://agno.com) framework (formerly Phidata).

## Prerequisites

1.  Python 3.10+
2.  Install dependencies:
    ```bash
    pip install agno google-genai python-dotenv beautifulsoup4 requests
    ```
3.  Ensure `.env` file is present in the root directory with `GEMINI_API_KEY` (or `GOOGLE_API_KEY`).

## Structure

-   `codeswarm/main.py`: The orchestrator script.
-   `codeswarm/agents.py`: Agent definitions (Admin, Dev, Revisor, AdminLogger).
-   `codeswarm/tools.py`: Tool definitions.
-   `codeswarm/models.py`: Pydantic models for structured output.
-   `codeswarm/config.py`: Configuration loading.
-   `codeswarm/prompts/`: Agent prompts and Knowledge Base (KB).
-   `AGENTS.md`: Operational rules and guidelines for agents.

## Running

Run the main module from the project root:

```bash
python -m codeswarm.main --goal "Your project goal" --path "your_project_path" --rounds 1
```

## Migration Notes

This project has been migrated from Google ADK to Agno. The legacy ADK code can be found in `archive/codeswarm_legacy/`.

-   Replaced `google-adk` Agents with `agno.agent.Agent`.
-   Replaced ADK Workflow with a custom Python orchestration loop in `main.py`.
-   Tools are defined as standalone functions and passed to Agno agents.
-   Prompts are loaded from `codeswarm/prompts/` and formatted for Agno.
-   Structured Output is handled using Pydantic models via `output_schema`.

## Current Status & Known Issues
See `docs/report.md` for a detailed analysis of the current state and identified issues.
Major pending tasks:
- Enable code execution for DevAgent.
- Implement feedback loop between Dev and Revisor.
- Integrate Knowledge Base files.
