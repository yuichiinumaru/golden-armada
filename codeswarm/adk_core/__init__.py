import sys
print("--- Diagnostic: Inside codeswarm/adk_core/__init__.py (Attempt 2) ---")
try:
    print("Attempting to import google.generativeai first...")
    import google.generativeai
    print(f"Successfully imported google.generativeai: {google.generativeai}")
except Exception as e_genai:
    print(f"Failed to import 'google.generativeai': {e_genai}")

try:
    print("Attempting to import google.adk...")
    import google.adk
    print(f"Found google.adk module: {google.adk}")
    if hasattr(google.adk, '__file__') and google.adk.__file__:
        print(f"google.adk module path: {google.adk.__file__}")
        # Add code to list the contents of the google.adk directory
        import os
        adk_package_path = os.path.dirname(google.adk.__file__)
        print(f"Contents of google.adk package directory ({adk_package_path}): {os.listdir(adk_package_path)}")
    elif hasattr(google.adk, '__path__'):
        print(f"google.adk is a namespace package. Paths: {list(google.adk.__path__)}")
        # If it's a namespace package, list contents of its paths
        import os
        for path_item in google.adk.__path__:
            print(f"Contents of google.adk namespace path ({path_item}): {os.listdir(path_item)}")
    else:
        print("google.adk module is a namespace package or has no __file__ and no __path__.")
    
    adk_dir_content = dir(google.adk)
    print(f"Is 'callbacks' in dir(google.adk)? {'callbacks' in adk_dir_content}")
    if 'callbacks' not in adk_dir_content:
        print(f"Full dir(google.adk): {adk_dir_content}")

except Exception as e_adk:
    print(f"Error during google.adk diagnostic imports: {e_adk}")

print("--- End Diagnostic (Attempt 2) ---")

# Original imports now attempted after the above
# from google.adk.callbacks import AbstractCallbackHandler # This will be removed
# from google.adk.events import Event # This will be removed

from typing import Optional, Dict, Any
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.models import LlmRequest, LlmResponse
# We might need google.genai.types if we need to construct Content objects,
# but for logging, we'll primarily be reading from LlmRequest/LlmResponse.

# --- Function-based Callbacks for Logging ---

def log_llm_start(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Logs information before an LLM call."""
    prompt_text = ""
    if llm_request.contents:
        # Attempt to get text from the last part of the last content item
        last_content = llm_request.contents[-1]
        if last_content.parts:
            # Iterate through parts to find text, as parts can be multimodal
            for part in last_content.parts:
                if hasattr(part, 'text') and part.text:
                    prompt_text = part.text
                    break
    elif llm_request.config and llm_request.config.system_instruction:
        # Fallback to system instruction if contents are empty
        system_instruction = llm_request.config.system_instruction
        if hasattr(system_instruction, 'parts') and system_instruction.parts:
            prompt_text = system_instruction.parts[0].text or ""
        elif isinstance(system_instruction, str):
            prompt_text = system_instruction
        # If system_instruction is neither a string nor has parts, prompt_text remains ""

    print(f"[LLM Start] Agent: {callback_context.agent_name}, Prompt: {prompt_text[:120]}...")
    return None # Allow ADK to proceed

def log_llm_end(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Logs information after an LLM call."""
    response_text = ""
    if llm_response.content and llm_response.content.parts:
        # Assuming the first part contains the primary text response
        # This might need adjustment if the response is multi-part or includes function calls
        primary_part = llm_response.content.parts[0]
        if hasattr(primary_part, 'text') and primary_part.text:
            response_text = primary_part.text
        elif hasattr(primary_part, 'function_call') and primary_part.function_call:
            response_text = f"FunctionCall: {primary_part.function_call.name}"
        # Add more conditions if other types of parts need to be logged
    elif llm_response.error_message:
        response_text = f"Error: {llm_response.error_message}"

    print(f"[LLM End] Agent: {callback_context.agent_name}, Response: {response_text[:120]}...")
    return None # Allow ADK to proceed

def log_tool_start(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Logs information before a tool is executed."""
    print(f"[Tool Start] Agent: {tool_context.agent_name}, Tool: {tool.name}, Input: {str(args)[:120]}")
    return None # Allow ADK to proceed

def log_tool_end(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """Logs information after a tool has executed."""
    # The tool_response is typically a dict, often with a 'result' key
    # For logging, converting the whole dict to string might be too verbose for complex results.
    # We'll log a snippet.
    response_snippet = str(tool_response)[:120]
    if isinstance(tool_response, dict) and 'result' in tool_response:
        response_snippet = str(tool_response['result'])[:120]

    print(f"[Tool End] Agent: {tool_context.agent_name}, Tool: {tool.name}, Output: {response_snippet}...")
    return None # Allow ADK to proceed

# The CodeSwarmLoggingHandler class is no longer needed and should be removed.
# class CodeSwarmLoggingHandler(AbstractCallbackHandler):
#     def on_llm_start(self, event: Event) -> None:
#         print(f"[LLM Start] Prompt: {event.data.get('prompt', '')[:120]}...")
#
#     def on_llm_end(self, event: Event) -> None:
#         print(f"[LLM End] Response: {str(event.data.get('response', ''))[:120]}...")
#
#     def on_tool_start(self, event: Event) -> None:
#         print(f"[Tool Start] Name: {event.data.get('tool_name')}, Input: {event.data.get('tool_input')}")
#
#     def on_tool_end(self, event: Event) -> None:
#         print(f"[Tool End] Output: {str(event.data.get('tool_output', ''))[:120]}...")
