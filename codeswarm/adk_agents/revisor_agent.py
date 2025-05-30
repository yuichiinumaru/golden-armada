from google.adk.agents import LlmAgent
# Removed line: # from google.adk.output_parsers import JsonOutputParser
from ..adk_config import REVISOR_MODEL_STR
from .prompts_adk import get_revisor_instruction_string
from ..adk_core.tool_definitions import revisor_tools_adk
from ..adk_core import log_llm_start, log_llm_end, log_tool_start, log_tool_end

def create_revisor_llm_agent(revisor_id: int, model_override=None, debug_mode=False):
    model = model_override if model_override else REVISOR_MODEL_STR
    return LlmAgent(
        name=f"RevisorAgentADK_{revisor_id}",
        instruction=get_revisor_instruction_string(revisor_id),
        model=model,
        tools=revisor_tools_adk,
        # output_parser=JsonOutputParser(), # This was already commented, ensuring it stays that way or is removed.
        output_key=f"revisor_text_output_{revisor_id}",
        before_model_callback=log_llm_start,
        after_model_callback=log_llm_end,
        before_tool_callback=log_tool_start,
        after_tool_callback=log_tool_end,
        **(dict(debug=True) if debug_mode else {}) # Pass debug=True if debug_mode is set
    )
 