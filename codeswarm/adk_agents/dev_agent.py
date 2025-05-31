from google.adk.agents import LlmAgent
from ..adk_config import DEV_MODEL_STR
from .prompts_adk import get_dev_instruction_string
from ..adk_core.tool_definitions import dev_tools_adk
# from ..adk_models import DevAgentFunctionToolCallOutput # REVERTED
from ..adk_core import log_llm_start, log_llm_end, log_tool_start, log_tool_end

def create_dev_llm_agent(dev_id: int, model_override=None):
    model = model_override if model_override else DEV_MODEL_STR
    return LlmAgent(
        name=f"DevAgentADK_{dev_id}",
        instruction=get_dev_instruction_string(dev_id),
        model=model,
        tools=dev_tools_adk,
        # output_model=DevAgentFunctionToolCallOutput, # REVERTED
        output_key=f"dev_text_output_{dev_id}", # REINSTATED
        before_model_callback=log_llm_start,
        after_model_callback=log_llm_end,
        before_tool_callback=log_tool_start, # These won't be hit if orchestrator calls tool directly
        after_tool_callback=log_tool_end
    )
