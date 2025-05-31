from google.adk.agents import LlmAgent
# We will not import GeminiModel directly for now, as LlmAgent handles model configuration.
# from google.adk.models import GeminiModel 
# No direct import of GenerationConfig needed here if passing through model_kwargs
# from google.generativeai.types import GenerationConfig 

from ..adk_config import ADMIN_MODEL_STR, ADMIN_MODEL_TEMPERATURE, DEV_MODEL_STR, DEV_MODEL_TEMPERATURE, REVISOR_MODEL_STR, REVISOR_MODEL_TEMPERATURE
from .prompts_adk import get_admin_instruction_string
from ..adk_core.tool_definitions import admin_tools_adk, dev_tools_adk, revisor_tools_adk
from ..adk_core import log_llm_start, log_llm_end, log_tool_start, log_tool_end
from ..adk_models import AdminTaskOutput # Keep for when output_model might be re-enabled

import json # For loading prompts from JSON
from pathlib import Path # For path manipulation for prompts

PROMPT_DIR = Path(__file__).parent.parent / "prompts"

def load_instruction_from_file(prompt_filename: str):
    try:
        with open(PROMPT_DIR / prompt_filename, "r", encoding="utf-8") as f:
            prompt_config = json.load(f)
        # The actual instruction might be under a specific key, e.g., "instruction" or "system_prompt"
        # Adjust based on your JSON structure. Let's assume it's directly the content for now,
        # or structured as {"instruction": "..."}
        if "instruction" in prompt_config:
            return prompt_config["instruction"]
        # Fallback for different structures or if the whole JSON is the prompt string
        elif isinstance(prompt_config, str):
             return prompt_config
        else: # If it's a dict but no 'instruction' key, convert whole dict to string
             return json.dumps(prompt_config)

    except FileNotFoundError:
        print(f"ERROR: Prompt file {prompt_filename} not found in {PROMPT_DIR}")
        return "Error: Prompt file not found." # Fallback instruction
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from {prompt_filename}")
        return "Error: Could not decode prompt JSON." # Fallback instruction

def create_admin_llm_agent(model_override=None, instruction_override: str = None, tools_override: list = None):
    model_name_to_use = model_override if model_override else ADMIN_MODEL_STR
    
    llm_generate_content_config = {
        "temperature": ADMIN_MODEL_TEMPERATURE,
    }
    
    current_instruction = instruction_override if instruction_override is not None else load_instruction_from_file("admin_prompt.json") # Default to original admin_prompt
    current_tools = tools_override if tools_override is not None else admin_tools_adk

    # Only set response_mime_type if there are no tools, as it can conflict with function calling
    if not current_tools:
        llm_generate_content_config["response_mime_type"] = "application/json"
        # This assumes that an agent without tools that needs to output JSON should have this.
        # If the instruction itself (like for the formatter) asks for JSON, this might be redundant or helpful.

    agent_parameters = {
        "name": "AdminAgentADK", # Consider making name more dynamic if multiple admin types are used frequently
        "model": model_name_to_use,
        "instruction": current_instruction,
        "tools": current_tools,
        "generate_content_config": llm_generate_content_config,
        # "output_model": AdminTaskOutput, # Temporarily removed to resolve Pydantic error
        "before_model_callback": log_llm_start,
        "after_model_callback": log_llm_end,
        "before_tool_callback": log_tool_start,
        "after_tool_callback": log_tool_end,
    }

    try:
        agent = LlmAgent(**agent_parameters)
        print(f"INFO: LlmAgent '{agent.name}' created successfully (model: {model_name_to_use}, output_model: AdminTaskOutput). generate_content_config: {llm_generate_content_config}")
        return agent
    except Exception as e:
        print(f"ERROR: LlmAgent creation failed for '{agent_parameters.get('name')}'. Error: {e}")
        print(f"Failed with agent_parameters: {agent_parameters}")
        raise

def create_dev_llm_agent(dev_id: int, model_override=None):
    model_to_use = model_override if model_override else DEV_MODEL_STR
    return LlmAgent(
        name=f"DevAgentADK_{dev_id}",
        model=model_to_use,
        instruction=load_instruction_from_file("dev_prompt.json"),
        tools=dev_tools_adk,
        before_model_callback=log_llm_start,
        after_model_callback=log_llm_end,
        before_tool_callback=log_tool_start,
        after_tool_callback=log_tool_end,
    )

def create_revisor_llm_agent(revisor_id: int, model_override=None):
    model_to_use = model_override if model_override else REVISOR_MODEL_STR
    return LlmAgent(
        name=f"RevisorAgentADK_{revisor_id}",
        model=model_to_use,
        instruction=load_instruction_from_file("revisor_prompt.json"),
        tools=revisor_tools_adk,
        before_model_callback=log_llm_start,
        after_model_callback=log_llm_end,
        before_tool_callback=log_tool_start,
        after_tool_callback=log_tool_end,
    )

# You'll need similar updates for create_dev_llm_agent and create_revisor_llm_agent
# if they also need strict JSON output and controlled temperature.
# For now, focus is on AdminAgent.
