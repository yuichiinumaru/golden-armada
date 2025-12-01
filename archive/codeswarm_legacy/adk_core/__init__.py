import sys
from unittest.mock import MagicMock

# --- Mocking for google.adk ---
# Create a mock for the top-level 'google' if it doesn't exist or to ensure it's a module we can add to
# For this environment, 'google' itself (as a namespace) should exist.
# We primarily need to ensure 'google.adk' and its submodules are properly mocked *before*
# any 'from google.adk...' imports are attempted within this file or by files importing this.

# Check if google.adk is already a real module (e.g., if ADK is actually installed)
# For the purpose of these tests, we assume it's NOT, so we mock.
if 'google.adk' not in sys.modules:
    google_dot_adk_mock = MagicMock()
    google_dot_adk_mock.__path__ = ['dummy_adk_path'] # Make it look like a package
    sys.modules['google.adk'] = google_dot_adk_mock

    # Mock submodules and ensure they are attributes of the parent mock
    agents_mock = MagicMock()
    agents_mock.__path__ = ['dummy_agents_path'] # Make it look like a package
    sys.modules['google.adk.agents'] = agents_mock
    google_dot_adk_mock.agents = agents_mock

    callback_context_mock = MagicMock()
    sys.modules['google.adk.agents.callback_context'] = callback_context_mock
    agents_mock.callback_context = callback_context_mock
    tools_mock = MagicMock()
    tools_mock.__path__ = ['dummy_tools_path']
    sys.modules['google.adk.tools'] = tools_mock
    google_dot_adk_mock.tools = tools_mock

    tool_context_mock = MagicMock()
    sys.modules['google.adk.tools.tool_context'] = tool_context_mock
    tools_mock.tool_context = tool_context_mock

    base_tool_mock = MagicMock()
    sys.modules['google.adk.tools.base_tool'] = base_tool_mock
    tools_mock.base_tool = base_tool_mock
    
    models_mock = MagicMock()
    models_mock.__path__ = ['dummy_models_path']
    sys.modules['google.adk.models'] = models_mock
    google_dot_adk_mock.models = models_mock

    sessions_mock = MagicMock()
    sessions_mock.__path__ = ['dummy_sessions_path']
    sys.modules['google.adk.sessions'] = sessions_mock
    google_dot_adk_mock.sessions = sessions_mock

    # Mock specific classes that are imported directly
    callback_context_mock.CallbackContext = MagicMock()
    tool_context_mock.ToolContext = MagicMock()
    base_tool_mock.BaseTool = MagicMock()
    models_mock.LlmRequest = MagicMock()
    models_mock.LlmResponse = MagicMock()
    sessions_mock.InMemorySessionService = MagicMock()
    agents_mock.LlmAgent = MagicMock() # For LlmAgent used in adk_agents/__init__.py

# --- End Mocking ---

from typing import Optional, Dict, Any
# These imports should now use the mocks defined above if google.adk is not genuinely available
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
