import json
import os
from pathlib import Path
from agno.agent import Agent
from agno.models.google import Gemini
from . import config
from . import tools
from .models import AdminTaskOutput, AdminLogUpdateOutput, DevAgentOutput, RevisorAgentOutput

PROMPT_DIR = Path(__file__).parent / "prompts"
KB_DIR = PROMPT_DIR / "kb"

def load_prompt(filename: str) -> dict:
    with open(PROMPT_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)

def load_kb_content(kb_files: list) -> str:
    content = []
    for kb_file in kb_files:
        try:
            with open(KB_DIR / kb_file, "r", encoding="utf-8") as f:
                kb_data = json.load(f)
                content.append(f"--- Knowledge Base Module: {kb_file} ---")
                content.append(json.dumps(kb_data, indent=2))
                content.append("--- End Module ---")
        except FileNotFoundError:
            pass # Or use logger if we import it here, but pass is fine for now to avoid circular import if logger imports config
    return "\n".join(content)

def format_instructions(prompt_data: dict, kb_files: list = None) -> str:
    instructions = []

    if kb_files:
        kb_content = load_kb_content(kb_files)
        instructions.append("INTERNAL KNOWLEDGE BASE (Reference this for reasoning and methodologies):")
        instructions.append(kb_content)

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
    # Admin uses Problem Solving Framework and core reasoning
    kb_files = ["kb_framework_problem_solving.json", "kb_core_reasoning.json"]
    instructions = format_instructions(prompt_data, kb_files=kb_files)

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
    # Dev uses Software Engineer operational KBs
    kb_files = ["kb_role_software_engineer.json", "kb_synergy_software_engineer_operational.json"]
    instructions = format_instructions(prompt_data, kb_files=kb_files)

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
    # Revisor uses Reasoning validation and software engineer synergy
    kb_files = ["kb_validation_reasoning.json", "kb_role_software_engineer.json"]
    instructions = format_instructions(prompt_data, kb_files=kb_files)

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

def get_planner_agent(model_id: str = config.ADMIN_MODEL_STR) -> Agent:
    prompt_data = load_prompt("planner_prompt.json")
    # Planner uses high-level frameworks
    kb_files = ["kb_framework_problem_solving.json", "kb_strategy_topdown.json"]
    instructions = format_instructions(prompt_data, kb_files=kb_files)

    return Agent(
        name="PlannerAgent",
        model=Gemini(id=model_id, api_key=config.GEMINI_API_KEY),
        instructions=instructions,
        tools=[tools.read_file, tools.write_file],
        markdown=True,
    )

def get_knowledge_agent(model_id: str = config.DEV_MODEL_STR) -> Agent:
    prompt_data = load_prompt("knowledge_prompt.json")
    # Knowledge agent focuses on extraction and reasoning
    kb_files = ["kb_synergy_files_extractor.json"]
    instructions = format_instructions(prompt_data, kb_files=kb_files)

    return Agent(
        name="KnowledgeAgent",
        model=Gemini(id=model_id, api_key=config.GEMINI_API_KEY),
        instructions=instructions,
        tools=[tools.search_files_content, tools.read_file, tools.list_folder_contents],
        markdown=True,
    )
