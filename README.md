# CodeSwarm: A Multi-Agent Coding Assistant

CodeSwarm is a multi-agent system built using the Google Agent Development Kit (ADK). It employs a team of AI agents—Admin, Developer, Revisor, and AdminLogger—to collaboratively work on coding projects based on user-defined goals. CodeSwarm leverages Gemini models for all LLM operations and is designed for tasks like code generation, modification, and review.

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

-   **Multi-Agent Collaboration**: Utilizes Admin, Developer, Revisor, and AdminLogger agents for a structured and iterative workflow.
-   **Google ADK Powered**: Built upon the Google ADK framework for direct Gemini model integration and agent orchestration (tested with `google-adk==1.1.1`).
-   **Gemini Models**: Configurable to use different Gemini models (e.g., `gemini-1.5-flash-latest`) for various agent roles via a `.env` file.
-   **Tool-Equipped Agents**: Agents can request tool execution (e.g., file I/O) managed by the orchestrator or use ADK-native tool calls.
-   **Orchestrator-Managed Workflow**: A central controller manages task distribution, agent invocation, and `session.state` for context sharing.
-   **CLI Controllable**: Initialize projects, define goals, and manage rounds via command-line arguments.
-   **Dynamic Project Handling**: Can work within a user-specified project directory.

## Project Structure

-   `codeswarm/main_adk_controller.py`: The main orchestration script that manages the agent workflow.
-   `codeswarm/adk_agents/`: Contains agent prompt definitions (JSON files) and agent creation logic.
-   `codeswarm/adk_core/`: Contains tool logic (`tool_logic.py`), ADK FunctionTool definitions, and ADK setup helpers.
-   `codeswarm/adk_config.py`: Loads `.env` variables and provides configuration for agents and tools.
-   `.env`: (Must be created manually in the project root) Stores API keys, model names, and critical paths.
-   `docs/`: Contains detailed documentation including project specifications, task lists, and development evolution.
-   `project_logs/`: Directory for operational logs like `changelog.log`.
-   `generated_code/`: A default directory where projects can be created if no specific path is given (configurable via `.env`).

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
    From within your activated conda environment and the project's root directory, run:
    ```bash
    pip install google-adk[extensions] google-genai python-dotenv requests beautifulsoup4
    ```
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
    # gemini-1.5-flash-latest is a known compatible model with ADK 1.1.1
    ADMIN_MODEL=gemini-1.5-flash-latest
    DEV_MODEL=gemini-1.5-flash-latest
    REVISOR_MODEL=gemini-1.5-flash-latest
    ADMIN_LOGGER_MODEL=gemini-1.5-flash-latest # If using a separate model for AdminLogger

    # Target project path for tools - crucial for security and proper file operations.
    # This should be an absolute path or a path relative to the project root.
    # Example: generated_code (will resolve to <project_root>/generated_code)
    TARGET_PROJECT_PATH_FOR_TOOLS=generated_code

    # Optional: Default project path if not specified via CLI
    # DEFAULT_PROJECT_PATH=generated_code/my_default_project
    ```
    **Note on `TARGET_PROJECT_PATH_FOR_TOOLS`**: This variable defines the secure base directory within which all file system tools will operate. It's critical for preventing tools from writing outside the intended project workspace.

## Running CodeSwarm

Execute the `main_adk_controller.py` script as a module from the **project root directory**. Ensure your conda environment is activated.

```bash
# Example:
# conda activate codeswarm_env # If not already active
# (Ensure you are in the project root directory where .env is located)

python -m codeswarm.main_adk_controller --goal "Your project goal here" --project_path "my_project"
```

**Command-Line Options:**

-   `--goal TEXT`: The overall project goal or initial task description. (Required)
-   `--project_path TEXT`: The name of the directory (relative to `TARGET_PROJECT_PATH_FOR_TOOLS`) where the agents will work. If it doesn't exist, it will be created. Example: "my_new_python_app". (Required)
-   `--pairs INTEGER`: Number of Dev/Revisor pairs. Default is 1.
-   `--rounds INTEGER`: Number of development/review rounds. Default is 1.
-   `--help`: Show help message and exit.

**Examples:**

1.  **Start a new project named "calculator_cli"**:
    ```bash
    python -m codeswarm.main_adk_controller --goal "Create a Python CLI application for a simple calculator" --project_path "calculator_cli"
    ```
    *(This will create and operate within `<project_root>/generated_code/calculator_cli` if `TARGET_PROJECT_PATH_FOR_TOOLS` is `generated_code`)*

2.  **Work on an existing project (assuming it's within the tool path)**:
    ```bash
    python -m codeswarm.main_adk_controller --goal "Refactor the main module and add unit tests" --project_path "existing_app" --pairs 1 --rounds 2
    ```

## How it Works

CodeSwarm operates through a structured workflow managed by the `main_adk_controller.py` orchestrator:

1.  **Initialization**:
    *   The user provides a project goal and parameters (e.g., `project_path`, number of agent pairs, rounds) via CLI.
    *   The orchestrator initializes the agents (Admin, Dev(s), Revisor(s), AdminLogger) and the ADK session, including `session.state` for sharing context.
    *   The `target_project_path` for the current run is established by combining `TARGET_PROJECT_PATH_FOR_TOOLS` from `.env` and the `--project_path` CLI argument.

2.  **Admin Task Definition (AdminAgent)**:
    *   The AdminAgent (potentially a two-step Interpreter/Formatter process) receives the overall goal and project context via `session.state`.
    *   It breaks down the goal into a list of specific, actionable tasks (e.g., "create file `foo.py` with specific content", "append a function to `bar.py`").
    *   Tasks are output as a JSON list. File paths in tasks are specified relative to the `target_project_path`.

3.  **Task Execution Loop (Orchestrator-led)**:
    *   The orchestrator iterates through the task list generated by the AdminAgent.
    *   For each task:
        *   **DevAgent Phase**:
            *   The assigned DevAgent receives the task description and relevant context (like absolute file paths for tools) via `session.state`.
            *   It generates code or text content.
            *   To perform actions like writing files, the DevAgent outputs a structured JSON `function_call` (e.g., `{"function_call": {"name": "write_file", "args": {"file_path": "path/to/file.py", "content": "...", "mode": "overwrite"}}}`).
            *   The orchestrator parses this JSON and executes the corresponding tool function from `tool_logic.py`, ensuring operations are within the `target_project_path`.
        *   **RevisorAgent Phase**:
            *   If the task involves review, the RevisorAgent receives the relevant file path (via `session.state`).
            *   It uses its tools (e.g., `read_file`, potentially ADK-native calls) to inspect the content and generates constructive feedback.

4.  **Logging (AdminLoggerAgent)**:
    *   After each round or significant set of tasks, the AdminLoggerAgent is invoked.
    *   It receives a summary of actions and updates `project_logs/changelog.log` with the status.

5.  **Iteration**:
    *   The process (Admin task definition -> Task Execution -> Logging) repeats for the specified number of rounds, allowing for iterative refinement.

## Important Notes

-   **File Path Management**:
    -   The `--project_path` CLI argument defines the specific sub-directory for the current run, relative to the `TARGET_PROJECT_PATH_FOR_TOOLS` defined in your `.env` file.
    -   `TARGET_PROJECT_PATH_FOR_TOOLS` in `.env` is the root directory for all tool operations, ensuring safety.
    -   AdminAgent generates tasks with relative paths; the orchestrator resolves these to absolute paths within the defined project scope before passing them to tools or agents via `session.state`.
-   **Tool Usage**: The clarity of prompts and, for ADK-native calls, tool docstrings in `codeswarm/adk_core/tool_logic.py` is crucial for LLMs to correctly request or use tools.
-   **Error Handling**: The system aims for robust error handling, but unexpected LLM outputs might require prompt refinement.
-   **Session State (`session.state`)**: This ADK feature is critical for passing information (like goals, file paths, and intermediate data) between the orchestrator and agents, and for grounding agent prompts.

## Further Information

-   **Project Specifications & Architecture**: [docs/project.md](docs/project.md)
-   **Current Tasks & Progress**: [docs/tasklist.md](docs/tasklist.md)
-   **Development Changelog**: [project_logs/changelog.log](project_logs/changelog.log)
-   **Detailed Technical Evolution & Lessons Learned**: [docs/codeswarm_development_evolution.md](docs/codeswarm_development_evolution.md)

## Roadmap & Future Ideas
(This section can be updated with future plans for CodeSwarm)
- Enhanced RAG capabilities for context-aware coding.
- More sophisticated inter-agent communication.
- Integration with version control systems.
- Advanced debugging tools for agent behavior.
