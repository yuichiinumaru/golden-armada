from pydantic import BaseModel, Field
from typing import List

class TaskAssignment(BaseModel):
    dev_id: int = Field(..., description="Identifier for the Dev agent.")
    revisor_id: int = Field(..., description="Identifier for the Revisor agent, typically the same as dev_id for a pair.")
    file_to_edit_or_create: str = Field(..., description="Absolute path to the file to be edited or created.")
    dev_task_description: str = Field(..., description="Detailed description of the task for the Dev agent.")
    revisor_focus_areas: str = Field(..., description="Specific areas for the Revisor agent to focus on during review.")

class AdminTaskOutput(BaseModel):
    tasks: List[TaskAssignment] = Field(default_factory=list, description="List of task assignments for Dev/Revisor pairs.")

class AdminLogUpdateOutput(BaseModel):
    status: str = Field(..., description="Status of the logging/update operation (e.g., 'success', 'error').")
    message: str = Field(..., description="A message detailing the outcome of the logging/update operation.")

# Pydantic model for the arguments of the write_file tool
class WriteFileArgs(BaseModel):
    file_path: str = Field(..., description="The absolute path to the file to be written.")
    content: str = Field(..., description="The content to write to the file.")

    # This uses a feature from a potential future version of ADK or a misunderstanding.
    # For google-adk==1.1.1, ToolConfig is typically not used this way directly in the model's config.
    # Instead, the LlmAgent is initialized with a list of tools (functions), and if the LLM
    # outputs a FunctionCall whose name matches one of these tools AND whose arguments
    # are compatible with that tool's signature (or a Pydantic model for its args), it's called.
    # The primary mechanism is the LLM outputting a FunctionCall object, not just a Pydantic model.
    # However, having a Pydantic model for tool arguments is good practice for validation if the
    # ADK's tool invoker uses it.
    # For now, this explicit ToolConfig might be ignored or cause issues if not supported by 1.1.1 in this exact way.
    # Let's assume for a moment the goal is to have the LLM output JSON matching this model,
    # and the orchestrator then makes the call. But the true goal is for the ADK to make the call.
    #
    # UPDATE: The ADK's LlmAgent can indeed take an `output_model` which, if it represents
    # the arguments of a tool known to the agent, should lead to that tool being called.
    # The key is that the LLM must output JSON that *is* these arguments, and the agent's instruction
    # must guide it to call the specific tool.

    # According to ADK team, for the agent to call a tool based on output_model,
    # the output_model should be the Pydantic model for the *arguments* of the tool,
    # and the LLM should be prompted to produce *just those arguments* as its JSON output,
    # while also being prompted to "call" the tool by name.
    # The ADK will then match the tool name from the LLM's intent (if expressed clearly
    # outside the JSON args) and use the output_model instance as its arguments.

    # Let's try without the explicit ToolConfig in model_config first,
    # as the primary mechanism is the agent's tool list and the LLM outputting a FunctionCall.
    # The Pydantic model for args is useful for the tool definition itself.
    # The issue is making the LLM *actually emit a FunctionCall object* or a structure
    # that the ADK recognizes as such.

    # Re-evaluating: The prompt for DevAgent already asks for a specific JSON structure
    # `{"function_call": {"name": "write_file", "args": {...}}}`.
    # The issue wasn't the *structure* but the ADK not acting on it.
    # The previous step (parsing this from output_text) made the orchestrator see it.
    # Now, how to make the ADK's internal tool invoker see it?

    # The `LlmAgent`'s `output_model` is for the *entire* response from the LLM.
    # If we want the LLM to output a function call, the `output_model` should be a Pydantic model
    # representing that function call structure.

class FunctionCallArgs(BaseModel):
    file_path: str
    content: str

class FunctionCall(BaseModel):
    name: str
    args: FunctionCallArgs

class DevAgentFunctionToolCallOutput(BaseModel):
    function_call: FunctionCall = Field(..., description="A function call to be executed by the system.")