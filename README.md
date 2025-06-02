# CodeSwarm: A Multi-Agent Coding System (ADK-based)

CodeSwarm is a multi-agent system built using the Google Agent Development Kit (ADK). It employs a team of AI agents—Admin, Developer, and Revisor—to collaboratively work on coding projects based on user-defined goals. CodeSwarm leverages Gemini models for all LLM operations and is designed for tasks like code generation, modification, and review.

## Overview

The primary goal of CodeSwarm is to implement a robust multi-agent system that can:
- Understand complex coding goals.
- Break them down into manageable tasks.
- Assign tasks to specialized agents.
- Facilitate code generation and modification.
- Conduct reviews of the generated code.
- Maintain a log of activities and project status.

For detailed project specifications, architecture, and agent roles, please see [docs/project.md](docs/project.md).

## Features

-   **Multi-Agent Collaboration**: Utilizes Admin, Developer, and Revisor agents for a structured and iterative workflow. The AdminAgent also handles logging tasks.
-   **Google ADK Powered**: Built upon the Google ADK framework for direct Gemini model integration and agent orchestration (tested with `google-adk==1.1.1`).
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
-   **Gemini Models**: Configurable to use different Gemini models (e.g., `gemini-1.5-flash-latest`) for various agent roles via a `.env` file.
-   **Pydantic Models**: Uses Pydantic models (e.g., `AdminTaskOutput`, `DevAgentOutput`, `RevisorAgentOutput`) for structured JSON communication between agents and the orchestrator.
-   **Tool-Equipped Agents**: Agents use ADK-native tool calls for operations like file I/O and web browsing, based on assigned `FunctionTool` definitions.
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
-   **Gemini Models**: Configurable to use different Gemini models (e.g., `gemini-2.5-flash-preview-05-20`) for various agent roles via a `.env` file.
-   **Tool-Equipped Agents**: Agents can request tool execution (e.g., file I/O) managed by the orchestrator or use ADK-native tool calls.
>>>>>>> Stashed changes
-   **Orchestrator-Managed Workflow**: A central controller manages task distribution, agent invocation, and `session.state` for context sharing.
-   **CLI Controllable**: Initialize projects, define goals, manage rounds, and override models via command-line arguments.
-   **Iterative Development**: Supports multiple rounds of development and review for refining outputs.
-   **Dynamic Project Handling**: Can work within a user-specified project directory.

## Project Structure

-   `codeswarm/main_adk_controller.py`: The main orchestration script that manages the agent workflow.
-   `codeswarm/adk_agents/`: Contains agent prompt definitions (JSON files) and agent creation logic.
-   `codeswarm/adk_core/`: Contains tool logic (`tool_logic.py`), ADK FunctionTool definitions, and ADK setup helpers.
-   `codeswarm/adk_config.py`: Loads `.env` variables and provides configuration for agents and tools.
-   `.env`: (Must be created manually in the project root) Stores API keys, model names, and the default project path.
-   `docs/`: Contains detailed documentation including project specifications, task lists (`tasklist.md`), development evolution, and primary logs (`changelog.log`).
-   `project_logs/`: Potentially for future detailed operational logs. Current primary logs like `changelog.log` and `tasklist.md` are in `docs/`.
-   `generated_code/`: A default directory that can be used as a parent for projects if `DEFAULT_PROJECT_PATH` or `--path` points into it.

## Prerequisites

1.  **Python**: Python 3.10 or higher (Python 3.11 recommended).
2.  **Conda (Recommended)**: For managing environments.
    ```bash
    # Create a new conda environment
    conda create -n codeswarm_env python=3.11
    conda activate codeswarm_env
    ```
3.  **Gemini API Key**: You need an active Gemini API key.
4.  **Required Python Packages**:
    From within your activated conda environment and the project's root directory, install the required packages using the `requirements.txt` file located in the `codeswarm` subdirectory:
    ```bash
    pip install -r codeswarm/requirements.txt
    ```
    This will install key dependencies such as `google-adk[extensions]`, `google-genai`, `a2a-sdk`, `python-dotenv`, `requests`, `beautifulsoup4`, and `pydantic` (which is a core component used for data validation and settings management within ADK and this project).
    (Ensure you are using a version of `google-adk` compatible with the project, e.g., `google-adk==1.1.1` as referenced in development docs.)

## Setup

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd codeswarm_project_root
    ```
2.  **Create `.env` File**: In the **project root directory**, create a `.env` file. This file is crucial for API keys, model configuration, and tool paths.
    ```env
    # .env
    GEMINI_API_KEY=your_actual_gemini_api_key_here

    # Specify the Gemini models for each agent role
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    # gemini-1.5-flash-latest is a known compatible model with ADK 1.1.1
    ADMIN_MODEL=gemini-1.5-flash-latest
    DEV_MODEL=gemini-1.5-flash-latest
    REVISOR_MODEL=gemini-1.5-flash-latest
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    # gemini-2.5-flash-preview-05-20 is a known compatible model with ADK 1.1.1
    ADMIN_MODEL=gemini-2.5-flash-preview-05-20
    DEV_MODEL=gemini-2.5-flash-preview-05-20
    REVISOR_MODEL=gemini-2.5-flash-preview-05-20
    ADMIN_LOGGER_MODEL=gemini-2.5-flash-preview-05-20 # If using a separate model for AdminLogger
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

    # Optional: Default project path if not specified via CLI's --path argument.
    # This should be an absolute path or a path relative to where you run the script.
    # Example: DEFAULT_PROJECT_PATH=generated_code/my_default_project
    # Example: DEFAULT_PROJECT_PATH=/path/to/your/projects/my_default_project
    DEFAULT_PROJECT_PATH=generated_code/my_default_project

    # Optional: Model temperatures (defaults may be set in adk_config.py if not specified here)
    # Values typically between 0.0 and 1.0
    # ADMIN_TEMPERATURE=0.5
    # DEV_TEMPERATURE=0.7
    # REVISOR_TEMPERATURE=0.4
    ```
    **Note on `DEFAULT_PROJECT_PATH`**: This variable in the `.env` file provides a default location for projects if the `--path` command-line argument is not used. The path specified by `--path` (or `DEFAULT_PROJECT_PATH` if `--path` is omitted) defines the root directory for the specific project run. All file operations performed by the agents (like reading, writing, or listing files) are confined within this designated project path to ensure security and organization.

## Running CodeSwarm

Execute the `main_adk_controller.py` script as a module from the **project root directory**. Ensure your conda environment is activated.

```bash
# Example:
# conda activate codeswarm_env # If not already active
# (Ensure you are in the project root directory where .env is located)

python -m codeswarm.main_adk_controller --goal "Your project goal here" --path "my_project"
```

**Command-Line Options:**

-   `--goal TEXT`: The overall project goal or initial task description. (Required)
-   `-P TEXT, --path TEXT`: Absolute or relative path to the project directory where agents will work. If it doesn't exist, it might be created. This path becomes the root for all file operations for the run. (Required, or defaults to `DEFAULT_PROJECT_PATH` from `.env` if set)
-   `--pairs INTEGER`: Number of Dev/Revisor pairs. Default is 1.
-   `--rounds INTEGER`: Number of development/review rounds. Default is 1.
-   `--model TEXT`: Optional. Override the Gemini model for all agents (e.g., `gemini-1.5-pro-latest`). If not set, uses models from `.env` or defaults in `adk_config.py`.
-   `--help`: Show help message and exit.

**Examples:**

1.  **Start a new project named "calculator_cli"**:
    ```bash
    python -m codeswarm.main_adk_controller --goal "Create a Python CLI application for a simple calculator" --path "calculator_cli"
    ```
    *(If `DEFAULT_PROJECT_PATH` is `generated_code/my_default_project` and `calculator_cli` is relative, this might operate in `generated_code/my_default_project/calculator_cli` or directly `calculator_cli` depending on current working directory and how `main_adk_controller.py` resolves it. It's generally safer to use absolute paths or ensure `DEFAULT_PROJECT_PATH` itself is a sensible parent if using relative `--path`.)*

2.  **Work on an existing project (e.g., in `projects/existing_app`)**:
    ```bash
    python -m codeswarm.main_adk_controller --goal "Refactor the main module and add unit tests" --path "projects/existing_app" --pairs 1 --rounds 2
    ```

## How it Works

CodeSwarm operates through a structured workflow managed by the `main_adk_controller.py` orchestrator:

1.  **Initialization**:
    *   The user provides a project goal and parameters (e.g., `--path`, number of agent pairs, rounds) via CLI.
    *   The orchestrator initializes the agents (Admin, Dev(s), Revisor(s)) and the ADK session, including `session.state` for sharing context.
    *   The `target_project_path` for the current run is established from the `--path` CLI argument (or `DEFAULT_PROJECT_PATH` from `.env` if `--path` is not provided). This path is the root for all project operations.

2.  **Admin Task Definition (AdminAgent)**:
    *   The AdminAgent receives the overall goal and project context (including the `target_project_path`) via `session.state`.
    *   It breaks down the goal into a list of specific, actionable tasks (e.g., "create file `foo.py` with specific content", "append a function to `bar.py`").
    *   Tasks are output as a JSON list. File paths in tasks are specified as absolute paths, constructed by the AdminAgent using the provided `target_project_path`.

3.  **Task Execution Loop (Orchestrator-led)**:
    *   The orchestrator iterates through the task list generated by the AdminAgent.
    *   For each task:
        *   **DevAgent Phase**:
            *   The assigned DevAgent receives the task description and the absolute `file_to_edit_or_create` via `session.state`.
            *   It generates code or text content.
            *   To perform actions like writing files, the DevAgent uses tools like `write_file` (which could be an ADK-native tool or a tool executed by the orchestrator based on agent output). The DevAgent is instructed to use the absolute file path provided in its task.
            *   The orchestrator (or ADK framework for native tools) ensures that all tool operations using these paths are confined within the `target_project_path` established for the run.
        *   **RevisorAgent Phase**:
            *   If the task involves review, the RevisorAgent receives the relevant absolute file path (via `session.state`).
            *   It uses its tools (e.g., `read_file`) to inspect the content and generates constructive feedback.

4.  **Logging (AdminAgent)**:
    *   After each round or significant set of tasks, the AdminAgent enters its 'logging_and_updates' phase.
    *   It receives a summary of actions and updates `docs/changelog.log` and `docs/tasklist.md` within the `target_project_path`.

5.  **Iteration**:
    *   The process (Admin task definition -> Task Execution -> Logging) repeats for the specified number of rounds, allowing for iterative refinement.

## Key Files

-   `codeswarm/main_adk_controller.py`: Main orchestrator script.
-   `codeswarm/adk_config.py`: Loads `.env` configurations.
-   `codeswarm/adk_agents/__init__.py`: Defines agent creation functions.
-   `codeswarm/prompts/`: Directory containing JSON prompt files for each agent.
-   `codeswarm/adk_core/__init__.py`: Core ADK setup, tool definitions, and callback functions.
-   `codeswarm/adk_core/tool_logic.py`: Python functions underlying the ADK tools.
-   `codeswarm/adk_models.py`: Defines Pydantic models for structured agent outputs (e.g., `AdminTaskOutput`).
-   `docs/tasklist.md`: Current development tasks and progress.
-   `docs/project.md`: Detailed project specifications and architecture.
-   `docs/changelog.log`: Log of significant changes and updates.

## Important Notes

-   **File Path Management**:
    -   The `--path` CLI argument (or `DEFAULT_PROJECT_PATH` from `.env`) defines the root directory for the current project run.
    -   All file system operations performed by agents via tools are confined to this path by the orchestrator and path validation logic.
    -   Agents (like AdminAgent and DevAgent) are expected to work with absolute paths that are constructed based on this root `target_project_path`.
-   **Tool Usage**: The clarity of prompts and, for ADK-native calls, tool docstrings in `codeswarm/adk_core/tool_logic.py` is crucial for LLMs to correctly request or use tools.
-   **Error Handling**: The system aims for robust error handling, but unexpected LLM outputs might require prompt refinement.
-   **Session State (`session.state`)**: This ADK feature is critical for passing information (like goals, file paths, and intermediate data) between the orchestrator and agents, and for grounding agent prompts.

## Further Information

-   **Project Specifications & Architecture**: [docs/project.md](docs/project.md)
-   **Current Tasks & Progress**: [docs/tasklist.md](docs/tasklist.md)
-   **Development Changelog**: [docs/changelog.log](docs/changelog.log)
-   **Detailed Technical Evolution & Lessons Learned**: [docs/codeswarm_development_evolution.md](docs/codeswarm_development_evolution.md)

## Roadmap & Future Ideas
(This section can be updated with future plans for CodeSwarm)
- Enhanced RAG capabilities for context-aware coding.
- More sophisticated inter-agent communication.
- Integration with version control systems.
- Advanced debugging tools for agent behavior.
