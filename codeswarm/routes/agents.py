from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from codeswarm.services.agent_factory import create_agent_file
from fastapi.responses import StreamingResponse
import asyncio
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["agents"])

def get_registry(request: Request):
    return request.app.state.agent_registry

class AgentListResponse(BaseModel):
    agents: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    agent_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    steps: List[str] = []

class CreateAgentRequest(BaseModel):
    name: str
    prompt: str
    model: str = "gemini-2.5-flash"

@router.get("/agents", response_model=AgentListResponse)
async def list_agents(request: Request):
    """List all available agents with details."""
    registry = get_registry(request)
    agents = registry.get_agents_info()
    return {"agents": agents}

@router.post("/agents")
async def create_agent(payload: CreateAgentRequest, request: Request):
    """Create a new agent dynamically."""
    try:
        success, message = create_agent_file(payload.name, payload.prompt, payload.model)
        if not success:
             raise HTTPException(status_code=400, detail=message)

        # Trigger reload of registry?
        registry = get_registry(request)
        # Assuming AgentRegistry has dynamic scanning capability
        if hasattr(registry, "_scan_dynamic_agents"):
             await registry._scan_dynamic_agents() # Trigger scan
        else:
             registry.load_agents() # Standard reload

        return {"status": "success", "message": f"Agent {payload.name} created. Registry updated."}
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/chat", response_model=ChatResponse)
async def chat_with_agent(request: Request, chat_request: ChatRequest):
    """Chat with a specific agent."""
    logger.info(f"Received chat request for agent_id: '{chat_request.agent_id}'")
    registry = get_registry(request)
    
    agent = registry.get_agent(chat_request.agent_id)
    if not agent:
        logger.warning(f"Agent '{chat_request.agent_id}' not found in registry.")
        raise HTTPException(status_code=404, detail=f"Agent '{chat_request.agent_id}' not found")
    
    try:
        if hasattr(agent, "chat"):
            result = await agent.chat(chat_request.message)
            return ChatResponse(
                # Ensure response is a string, handle dict returns if any
                response=result.get("response", "") if isinstance(result, dict) else str(result),
                steps=result.get("steps", []) if isinstance(result, dict) else []
            )
        elif hasattr(agent, "run_task"):
             response_data = await agent.run_task(chat_request.message)
             if isinstance(response_data, dict):
                return ChatResponse(
                    response=response_data.get("response", ""),
                    steps=response_data.get("steps", [])
                )
             else:
                return ChatResponse(
                    response=str(response_data),
                    steps=[]
                )
        else:
             # Fallback to standard Agno methods or raise
             raise HTTPException(status_code=500, detail=f"Agent {chat_request.agent_id} does not support chat or run_task")

    except Exception as e:
        logger.error(f"Error during chat with {chat_request.agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/stream")
async def stream_agent_chat(request: Request, chat_request: ChatRequest):
    """Chat with an agent and stream events (SSE)."""
    logger.info(f"Received stream request for agent_id: '{chat_request.agent_id}'")
    registry = get_registry(request)
    
    agent = registry.get_agent(chat_request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{chat_request.agent_id}' not found")

    async def event_generator():
        queue = asyncio.Queue()
        
        async def status_callback(status: str, detail: str = ""):
            await queue.put({"type": "status", "agent": chat_request.agent_id, "status": status, "message": detail})
            
        async def run_agent_task():
            try:
                # 1. Custom Streaming Interface (Preferred)
                if hasattr(agent, "chat_stream"):
                    async for event in agent.chat_stream(chat_request.message):
                        await queue.put(event)
                
                # 2. Fallback to standard chat
                else:
                    await queue.put({"type": "status", "agent": chat_request.agent_id, "status": "working", "message": "Processing..."})
                    
                    if hasattr(agent, "chat"):
                        result = await agent.chat(chat_request.message)
                        await queue.put({"type": "response", "content": result.get("response", ""), "steps": result.get("steps", [])})
                    else:
                        await queue.put({"type": "error", "message": "Agent does not support chat"})
                        
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                await queue.put({"type": "error", "message": str(e)})
            finally:
                await queue.put(None) # Sentinel to stop stream

        # Start the background task
        asyncio.create_task(run_agent_task())

        # Yield events from the queue
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
