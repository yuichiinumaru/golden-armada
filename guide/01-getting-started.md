# Getting Started with CodeSwarm

This guide covers the prerequisites, installation, and basic usage of the CodeSwarm system.

## Prerequisites

*   **Python 3.10+**: Ensure you have a compatible Python version installed.
    *   Verify with: `python --version`
*   **Google Gemini API Key**: CodeSwarm uses Google's Gemini models via the `google-genai` library. You need a valid API key.

## Installation

1.  **Clone the Repository** (if applicable):
    ```bash
    git clone <repository-url>
    cd codeswarm
    ```

2.  **Install Dependencies**:
    CodeSwarm relies on several Python packages defined in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
    *   **Core Dependencies**:
        *   `agno`: The agent framework.
        *   `google-genai`: For LLM inference.
        *   `python-dotenv`: For loading environment variables.
        *   `beautifulsoup4` & `requests`: For web fetching tools.

## Configuration

CodeSwarm requires an environment file to manage secrets and settings.

1.  **Create a `.env` file** in the project root:
    ```bash
    touch .env
    ```

2.  **Add your API Key**:
    Open `.env` and add your Google API key.
    ```env
    GEMINI_API_KEY=your_api_key_here
    # Optional: If using other Agno tools that require GOOGLE_API_KEY
    GOOGLE_API_KEY=your_api_key_here
    ```
    *See [Configuration Reference](./05-configuration-reference.md) for all available options.*

## Hello World: Your First Run

To verify the installation, run CodeSwarm with a simple goal.

### Command Structure

The entry point is `codeswarm/main.py`.

```bash
python -m codeswarm.main --goal "Your Goal" --path "Target Directory"
```

### Example

Run the following command to generate a simple "Hello World" Python script:

```bash
python -m codeswarm.main \
  --goal "Create a Python script that prints 'Hello, CodeSwarm!'" \
  --path "./output/hello_world" \
  --rounds 1
```

### What Happens?

1.  **Initialization**: `AgentOS` initializes agents and loads the `.env` configuration (`codeswarm/agent_os.py`).
2.  **Planning**: The `AdminAgent` creates a task to write the script.
3.  **Execution**: The `DevAgent` writes the code, and the `RevisorAgent` reviews it.
4.  **Output**: The resulting code will be saved in `./output/hello_world/`.

### Troubleshooting

*   **Error: `Module not found`**: Ensure you are running the command from the repository root, not inside `codeswarm/`.
*   **Error: `API Key not found`**: Double-check your `.env` file location and content.
