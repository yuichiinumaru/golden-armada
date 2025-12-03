import json
import os
from pathlib import Path
from agno.agent import Agent
from agno.models.google import Gemini
from . import config
from . import tools
from .models import AdminTaskOutput, AdminLogUpdateOutput, DevAgentOutput, RevisorAgentOutput

PROMPT_DIR = Path(__file__).parent / "prompts"

def load_prompt(filename: str) -> dict:
    with open(PROMPT_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)

def format_instructions(prompt_data: dict) -> str:
    instructions = []

    if "explicit_processing_instruction" in prompt_data:
        instructions.append(prompt_data["explicit_processing_instruction"])

    if "agentProfile" in prompt_data:
        profile = prompt_data["agentProfile"]
        instructions.append(f"Role: {profile.get('role', '')}")

    if "coreDirectives" in prompt_data:
        instructions.append("Core Directives:")
        for d in prompt_data["coreDirectives"]:
            if isinstance(d, dict):
                # Handle complex directive object
                if "directive" in d:
                    instructions.append(f"- {d['directive']}")
                if "condition" in d:
                    instructions.append(f"  Condition: {d['condition']}")
                if "action" in d:
                    instructions.append(f"  Action: {d['action']}")
            else:
                instructions.append(f"- {d}")

    if "generalRules" in prompt_data:
        instructions.append("General Rules:")
        for rule in prompt_data["generalRules"]:
            instructions.append(f"- {rule}")

    if "critical_instruction" in prompt_data:
        instructions.append(f"CRITICAL: {prompt_data['critical_instruction']}")

    return "\n".join(instructions)

def get_admin_agent(model_id: str = config.ADMIN_MODEL_STR) -> Agent:
    prompt_data = load_prompt("admin_prompt.json")
    instructions = format_instructions(prompt_data)

    return Agent(
        name="AdminAgent",
        model=Gemini(id=model_id, api_key=config.GEMINI_API_KEY),
        instructions=instructions,
        tools=[tools.read_file, tools.write_file, tools.list_folder_contents,
               tools.search_files_content, tools.fetch_web_page_text_content,
               tools.chunk_file, tools.summarize_chunks],
        output_schema=AdminTaskOutput,
        structured_outputs=True,
        markdown=False, # We want structured JSON output primarily
    )

def get_admin_logger_agent(model_id: str = config.ADMIN_MODEL_STR) -> Agent:
    prompt_data = load_prompt("admin_prompt.json")
    instructions = format_instructions(prompt_data)

    return Agent(
        name="AdminLoggerAgent",
        model=Gemini(id=model_id, api_key=config.GEMINI_API_KEY),
        instructions=instructions,
        tools=[tools.read_file, tools.write_file, tools.list_folder_contents],
        output_schema=AdminLogUpdateOutput,
        structured_outputs=True,
        markdown=False,
    )

def get_dev_agent(dev_id: int, model_id: str = config.DEV_MODEL_STR) -> Agent:
    prompt_data = load_prompt("dev_prompt.json")
    instructions = format_instructions(prompt_data)

    # Inject dev_id into instructions if needed, though the prompt says it's in input.
    # The prompt says: "Your specific ID will be provided in the task input."

    return Agent(
        name=f"DevAgent_{dev_id}",
        model=Gemini(id=model_id, api_key=config.GEMINI_API_KEY),
        instructions=instructions,
        tools=[tools.read_file, tools.write_file, tools.list_folder_contents,
               tools.search_files_content, tools.chunk_file, tools.execute_python_code],
        output_schema=DevAgentOutput,
        structured_outputs=True,
    )

def get_revisor_agent(revisor_id: int, model_id: str = config.REVISOR_MODEL_STR) -> Agent:
    prompt_data = load_prompt("revisor_prompt.json")
    instructions = format_instructions(prompt_data)

    return Agent(
        name=f"RevisorAgent_{revisor_id}",
        model=Gemini(id=model_id, api_key=config.GEMINI_API_KEY),
        instructions=instructions,
        tools=[tools.read_file, tools.list_folder_contents,
               tools.fetch_web_page_text_content, tools.chunk_file,
               tools.summarize_chunks],
        output_schema=RevisorAgentOutput,
        structured_outputs=True,
    )
