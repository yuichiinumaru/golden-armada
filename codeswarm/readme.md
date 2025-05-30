# CodeSwarm: ADK/A2A Multi-Agent Coding Project

CodeSwarm is a multi-agent system built using the Google ADK (Agent Development Kit) and optionally the A2A protocol. It utilizes a team of AI agents (Admin, Developers, Revisors) to collaboratively work on coding projects based on user-defined goals, leveraging Gemini models for all LLM operations.

## Features

-   **Multi-Agent Collaboration**: Employs Admin, Developer, and Revisor agents for a structured workflow.
-   **Google ADK Powered**: Leverages the Google ADK framework for direct Gemini model integration and robust agent orchestration.
-   **Gemini Models**: Configurable to use different Gemini models for different agent roles via a `.env` file.
-   **Tool-Equipped Agents**: Agents use ADK FunctionTools for file I/O (read, write, list, search) and web browsing.
-   **Round-Based Workflow**: Iteratively refines code through development and review cycles.
-   **CLI Controllable**: Manage project initialization, goals, and iterations via command-line arguments.
-   **Dynamic Project Handling**: Can start new projects or work on existing ones.

## Project Structure

-   `main_adk_controller.py`: The main orchestration script that manages the agent workflow using ADK.
-   `adk_agents/`: Contains agent prompt definitions and agent creation functions for Admin, Dev, and Revisor agents.
-   `adk_core/`: Contains tool logic, ADK FunctionTool definitions, and ADK setup helpers.
-   `adk_config.py`: Loads `.env` variables (API keys, model names) and provides configuration for all agents.
-   `.env`: (Must be created manually) Stores API keys and agent model configurations. See "Setup" for details.
-   `project_logs/`: Directory containing `changelog.log`, `tasklist.md`, and `doclinks.md`.
-   `generated_code/`: Default directory where new projects initiated by CodeSwarm will be created.

## Prerequisites

1.  **Python**: Python 3.10 or higher.
2.  **Conda (Recommended)**: For managing environments.
    ```bash
    # Create a new conda environment (e.g., codeswarm_adk)
    conda create -n codeswarm_adk python=3.11 # Or your preferred Python 3.10+ version
    conda activate codeswarm_adk
    ```
3.  **WSL (for Windows Users)**: Recommended if you prefer to run Python projects within a Linux environment on Windows.
4.  **Gemini API Key**: You need a Gemini API key.
5.  **Required Python Packages**:
    From within your activated `codeswarm_adk` conda environment and the `codeswarm` project directory, run:
    ```bash
    pip install google-generativeai-adk python-dotenv requests beautifulsoup4
    ```

## Setup

1.  **Clone/Download CodeSwarm**: Ensure you have the `codeswarm` project directory.
2.  **Navigate to Project Directory**:
    ```bash
    cd /path/to/your/codeswarm_project/codeswarm
    ```
3.  **Create `.env` File**: In the `codeswarm/` directory, create a `.env` file with the following content, replacing placeholders with your actual values:
    ```env
    GEMINI_API_KEY=your_actual_gemini_api_key_here
    ADMIN_MODEL_TYPE=gemini-1.5-pro-latest
    DEV_MODEL_TYPE=gemini-1.5-flash-latest
    REVISOR_MODEL_TYPE=gemini-1.5-flash-latest
    ```
    You can adjust the `MODEL_TYPE` variables as needed if you want to experiment with different Gemini models for each role.

## Running CodeSwarm

Execute the `main_adk_controller.py` script from the `codeswarm/` directory. Ensure your conda environment is activated. If using WSL, ensure you are in your WSL terminal.

```bash
# Example:
# conda activate codeswarm_adk # If not already active
# cd /path/to/your/codeswarm_project/codeswarm

python main_adk_controller.py --goal "Your project goal here" --path /absolute/path/to/project --pairs 1 --rounds 2
```

**Command-Line Options:**

-   `--goal TEXT`: The overall project goal or initial task description. (Required)
-   `--path TEXT`: Absolute path to an existing project folder the agents will work in. (Required)
-   `--pairs INTEGER`: Number of Dev/Revisor pairs. Default is 1.
-   `--rounds INTEGER`: Number of editing rounds. Default is 1.
-   `--help`: Show help message and exit.

**Examples:**

1.  **Start a new project:**
    ```bash
    python main_adk_controller.py --goal "Create a Python script to parse CSV files" --path /absolute/path/to/new/project --pairs 1 --rounds 2
    ```

2.  **Work on an existing project:**
    ```bash
    python main_adk_controller.py --goal "Refactor the main module and add unit tests" --path /absolute/path/to/existing/project --pairs 2 --rounds 3
    ```

## How it Works

1.  **Initialization**: The user provides a project goal and parameters (number of agent pairs, rounds, project path) via CLI arguments. The system determines the `target_project_path`.
2.  **Admin Task Definition**: The `AdminAgent` receives the overall goal, the `target_project_path`, and the content of current log files (`tasklist.md`, `changelog.log`). It breaks down the goal into specific, actionable coding tasks and review instructions for Dev/Revisor pairs, outputting them in a structured JSON format. These tasks include file paths relative to the `target_project_path`.
3.  **Dev/Revisor Cycle (per pair)**:
    *   **Dev Phase**: A `DevAgent` receives a task description (including a target file path within the `target_project_path`) from the Admin. It writes new code or modifies existing code. The agent is expected to output the complete code content for the specified file. The orchestrator then uses the `write_file` tool to save this content to the actual file system at `target_project_path/filename.py`.
    *   **Revisor Phase**: A `RevisorAgent` receives the file path (of the code just modified by its paired DevAgent) and review instructions. It uses `read_file` to get the code and `fetch_web_page_text_content` (if needed, to consult URLs from `doclinks.md`) to review. It generates constructive feedback.
4.  **Admin Logging**: The `AdminAgent` collects all Dev outputs (e.g., confirmation of file write path) and Revisor feedback for the current round. It uses its `write_file` tool to update `project_logs/changelog.log` and `project_logs/tasklist.md`.
5.  **Iteration**: The process repeats for the specified number of rounds.
6.  **User Feedback Loop**: After the initial set of rounds completes, the user is prompted to review the state and can provide a new high-level prompt/adjustments and specify more rounds, or choose to terminate.

## Important Notes

-   **File Paths**:
    -   When working with existing projects (`--path`), ensure the provided path is absolute. Agents will then operate on files within this existing structure.
    -   For new projects (no `--path` specified), CodeSwarm creates a new sub-directory inside `codeswarm/generated_code/`. All agent file operations will be relative to this newly created project folder.
    -   The `AdminAgent` is responsible for defining the correct file paths for `DevAgent` tasks, considering whether it's an existing project or a new one.
-   **Tool Docstrings**: The clarity of docstrings in `adk_core/tool_logic.py` is crucial for the LLM agents to correctly understand and use the tools. "Args:" sections should be complete.
-   **Error Handling**: The system includes robust error handling for tools and agent execution. However, complex or unexpected LLM outputs (e.g., malformed JSON from AdminAgent, or agent failing to use tools as instructed) might require observation and potential refinement of system prompts or manual intervention.
-   **JSON from AdminAgent**: The `AdminAgent` is instructed to output tasks in a clean JSON list format. The `main_adk_controller.py` includes logic to parse this output.