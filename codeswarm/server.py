from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from codeswarm.routes.orchestrator import router as orchestrator_router
from codeswarm.routes.agents import router as agents_router
from codeswarm.routes.khala import router as khala_router
from codeswarm.core.registry import AgentRegistry
from codeswarm.deps import get_vivi_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Registry Instance
agent_registry = AgentRegistry()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Registry
    # Assuming AgentRegistry has initialize/shutdown methods or we add them
    # For now, simplistic approach
    logger.info("Initializing Agent Registry...")
    # agent_registry.initialize() # If needed
    app.state.agent_registry = agent_registry
    yield
    logger.info("Shutting down Agent Registry...")
    # await agent_registry.shutdown() # If needed

app = FastAPI(title="CodeSwarm AgentOS", version="1.0.0", lifespan=lifespan)

# Add CORS Middleware
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(orchestrator_router)
app.include_router(agents_router)
app.include_router(khala_router, prefix="/api")

class AgentRequest(BaseModel):
    agent_id: str
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health_check():
    vivi = await get_vivi_agent()
    return {
        "status": "healthy", 
        "service": "agent-os", 
        "agent_initialized": vivi is not None,
        "mapped_agents": list(agent_registry.agents.keys()) # infer keys
    }

@app.post("/api/v1/agent/run")
async def run_agent(request: AgentRequest, x_user_id: Optional[str] = Header(None)):
    user_id = x_user_id or "default_user"
    logger.info(f"Received request for agent {request.agent_id} from user {user_id}")
    
    agent = agent_registry.get_agent(request.agent_id)
    vivi_agent = await get_vivi_agent()

    if not agent:
        # Fallback logic
        logger.warning(f"Agent ID {request.agent_id} not found, falling back to Vivi.")
        if not vivi_agent:
             raise HTTPException(status_code=503, detail="Agent not initialized")

        try:
            # Assuming Vivi has .run() or .chat() compatible with Agno
            # We need to standardize on .run() which returns RunResponse or similar
            if hasattr(vivi_agent, "run_task"):
                chat_result = await vivi_agent.run_task(request.message)
                return {
                    "agent_id": request.agent_id,
                    "response": chat_result.get("response", "") if isinstance(chat_result, dict) else str(chat_result),
                    "steps": chat_result.get("steps", []) if isinstance(chat_result, dict) else [],
                    "warning": f"Agent {request.agent_id} not found, used fallback."
                }
            elif hasattr(vivi_agent, "run"):
                 chat_result = vivi_agent.run(request.message)
                 return {
                    "agent_id": request.agent_id,
                    "response": chat_result.content,
                    "steps": [], # parsing steps from Agno run response if needed
                    "warning": f"Agent {request.agent_id} not found, used fallback."
                }
            else:
                 raise HTTPException(status_code=500, detail="Fallback agent does not support running task")

        except Exception as e:
            logger.error(f"Error running fallback agent: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Handle Agent Execution
    try:
        # Check if it's the Vivi instance
        if agent == vivi_agent:
             # Logic for Vivi
             if hasattr(vivi_agent, "run_task"):
                 chat_result = await vivi_agent.run_task(request.message)
                 return {
                    "agent_id": request.agent_id,
                    "response": chat_result.get("response", ""),
                    "steps": chat_result.get("steps", [])
                }
             elif hasattr(vivi_agent, "run"):
                 chat_result = vivi_agent.run(request.message)
                 return {
                    "agent_id": request.agent_id,
                    "response": chat_result.content,
                    "steps": []
                }

        # It's a Golden Armada agent
        # Assuming all mapped agents have run_task method or match Agno interface
        if hasattr(agent, 'run_task'):
            response_data = await agent.run_task(request.message)
            if isinstance(response_data, dict):
                return {
                    "agent_id": request.agent_id,
                    "response": response_data.get("response", ""),
                    "steps": response_data.get("steps", [])
                }
            else:
                return {
                    "agent_id": request.agent_id,
                    "response": str(response_data),
                    "steps": []
                }
        elif hasattr(agent, "run"):
             # Agno Agent
             response_data = agent.run(request.message)
             return {
                 "agent_id": request.agent_id,
                 "response": response_data.content,
                 "steps": [] # Extra step parsing if needed
             }
        else:
             raise HTTPException(status_code=500, detail=f"Agent {request.agent_id} does not support run_task or run")

    except Exception as e:
        logger.error(f"Error running agent {request.agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
