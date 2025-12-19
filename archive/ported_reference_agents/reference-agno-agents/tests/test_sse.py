import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from app.main import app
import json

@pytest.mark.asyncio
async def test_agent_stream_endpoint():
    # Mock the registry and agent
    mock_agent = AsyncMock()
    
    # Define a custom async generator for the agent's chat_stream
    async def mock_chat_stream(message):
        yield {"type": "status", "agent": "test-agent", "status": "working", "message": "Thinking..."}
        yield {"type": "response", "content": "Hello world"}

    mock_agent.chat_stream = mock_chat_stream
    
    with patch("app.main.agent_registry.get_agent") as mock_get_agent:
        mock_get_agent.return_value = mock_agent
        
        with TestClient(app) as client:
            response = client.post("/api/v1/agent/stream", json={
                "agent_id": "test-agent",
                "message": "Hello",
                "context": {}
            })
            
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]
            
            # Read the stream content
            content = response.content.decode("utf-8")
            events = content.strip().split("\n\n")
            
            assert len(events) >= 2
            
            # Parse first event
            event1 = json.loads(events[0].replace("data: ", ""))
            assert event1["type"] == "status"
            assert event1["status"] == "working"
            
            # Parse second event
            event2 = json.loads(events[1].replace("data: ", ""))
            assert event2["type"] == "response"
            assert event2["content"] == "Hello world"
