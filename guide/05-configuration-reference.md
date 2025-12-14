# Configuration Reference

This document details the configuration options available in `codeswarm/config.py`. These settings are loaded from the `.env` file or system environment variables.

## API Keys

| Variable | Description | Required |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | The API key for Google's Gemini models. | **Yes** |
| `GOOGLE_API_KEY` | Alternate key used by some Agno tools. Defaults to `GEMINI_API_KEY` if not set. | No |

## Model Selection

You can configure the specific Gemini model used for each role. Default is `gemini-2.5-flash`.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `ADMIN_MODEL_TYPE` | Model for the Admin/Planner agent. | `gemini-2.5-flash` |
| `DEV_MODEL_TYPE` | Model for the Developer agent. | `gemini-2.5-flash` |
| `REVISOR_MODEL_TYPE` | Model for the Revisor agent. | `gemini-2.5-flash` |

## Model Parameters

Adjust the creativity/randomness of the agents.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `ADMIN_MODEL_TEMPERATURE` | Temperature for planning (lower is more deterministic). | `0.2` |
| `DEV_MODEL_TEMPERATURE` | Temperature for coding. | `0.3` |
| `REVISOR_MODEL_TEMPERATURE` | Temperature for reviewing. | `0.3` |

## Operational Defaults

These control the default behavior if command-line arguments are not provided.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DEFAULT_PROJECT_PATH` | Where generated code is stored. | `./generated_code` |
| `DEFAULT_GOAL` | The default project goal. | "Develop a simple Python script." |
| `DEFAULT_PAIRS` | Number of concurrent Dev/Revisor pairs. | `1` |
| `DEFAULT_ROUNDS` | Number of development rounds to run. | `1` |

## Missing Configuration

*   **API Keys**: If `GEMINI_API_KEY` is missing, the `Agno` framework will likely raise an authentication error when an agent attempts to initialize or run.
*   **Paths**: If `DEFAULT_PROJECT_PATH` is missing or invalid, the system defaults to `./generated_code`.
