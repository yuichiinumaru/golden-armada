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