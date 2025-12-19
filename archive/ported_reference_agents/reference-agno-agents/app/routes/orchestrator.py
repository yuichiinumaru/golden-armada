from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.deps import get_orchestrator_agent
from app.agents.orchestrator import OrchestratorAgent

router = APIRouter(prefix="/api/v1/orchestrator", tags=["orchestrator"])

class PlanRequest(BaseModel):
    user_request: str
    language: str = "en-us"

class ReviewRequest(BaseModel):
    instruction: str
    deliverables: List[str]
    output: str

class ReportRequest(BaseModel):
    original_request: str
    completed_steps: List[Dict[str, Any]]
    language: str = "en-us"

@router.post("/plan")
async def plan_workflow(
    request: PlanRequest,
    agent: OrchestratorAgent = Depends(get_orchestrator_agent)
):
    """Generate an execution plan for a user request."""
    try:
        return await agent.plan_workflow(request.user_request, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review")
async def review_output(
    request: ReviewRequest,
    agent: OrchestratorAgent = Depends(get_orchestrator_agent)
):
    """Review a task output against deliverables."""
    try:
        return await agent.review_task_output(request.instruction, request.deliverables, request.output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
async def generate_report(
    request: ReportRequest,
    agent: OrchestratorAgent = Depends(get_orchestrator_agent)
):
    """Generate a final executive report."""
    try:
        report = await agent.generate_final_report(request.original_request, request.completed_steps)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
