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

from app.routes.orchestrator import router as orchestrator_router
from app.routes.agents import router as agents_router
from app.routes.khala import router as khala_router
from app.services.agent_registry import AgentRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Registry Instance
agent_registry = AgentRegistry()

import sys
import app

# Alias agent_os to app to support agents importing from agent_os
sys.modules["agent_os"] = app

logger.info(f"DEBUG: app package location: {app.__file__}")
logger.info(f"DEBUG: sys.path: {sys.path}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await agent_registry.initialize()
    app.state.agent_registry = agent_registry
    yield
    await agent_registry.shutdown()

app = FastAPI(title="VIVI AgentOS", version="1.0.0", lifespan=lifespan)

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
    return {
        "status": "healthy", 
        "service": "agent-os", 
        "agent_initialized": agent_registry.get_vivi_agent() is not None,
        "mapped_agents": agent_registry.get_mapped_agents_ids()
    }

@app.post("/api/v1/agent/run")
async def run_agent(request: AgentRequest, x_user_id: Optional[str] = Header(None)):
    user_id = x_user_id or "default_user"
    logger.info(f"Received request for agent {request.agent_id} from user {user_id}")
    
    agent = agent_registry.get_agent(request.agent_id)
    vivi_agent = agent_registry.get_vivi_agent()

    if not agent:
        # Fallback logic
        logger.warning(f"Agent ID {request.agent_id} not found, falling back to Vivi.")
        if not vivi_agent:
             raise HTTPException(status_code=503, detail="Agent not initialized")

        try:
            chat_result = await vivi_agent.chat(request.message, user_id=user_id)
            return {
                "agent_id": request.agent_id,
                "response": chat_result["response"],
                "steps": chat_result["steps"],
                "warning": f"Agent {request.agent_id} not found, used fallback."
            }
        except Exception as e:
            logger.error(f"Error running fallback agent: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Handle Agent Execution
    try:
        # Check if it's the Vivi instance
        if agent == vivi_agent:
             chat_result = await vivi_agent.chat(request.message, user_id=user_id)
             return {
                "agent_id": request.agent_id,
                "response": chat_result["response"],
                "steps": chat_result["steps"]
            }

        # It's a Golden Armada agent
        # Assuming all mapped agents have run_task method
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
        else:
             raise HTTPException(status_code=500, detail=f"Agent {request.agent_id} does not support run_task")

    except Exception as e:
        logger.error(f"Error running agent {request.agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
