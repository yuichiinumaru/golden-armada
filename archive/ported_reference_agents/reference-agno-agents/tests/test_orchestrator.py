from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock, patch

# Remove global client
# client = TestClient(app)

# Mock initialization to avoid DB connection
# Mock initialization to avoid DB connection
def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@patch("app.agents.orchestrator.OrchestratorAgent.plan_workflow")
def test_plan_workflow(mock_plan):
    mock_plan.return_value = {"thoughts": "Test plan", "steps": []}
    
    with TestClient(app) as client:
        response = client.post("/api/v1/orchestrator/plan", json={
            "user_request": "Test request",
            "language": "en-us"
        })
        
        assert response.status_code == 200
        assert response.json()["thoughts"] == "Test plan"

@patch("app.agents.orchestrator.OrchestratorAgent.review_task_output")
@patch("app.agents.orchestrator.OrchestratorAgent.initialize")
def test_review_output(mock_orch_init, mock_review):
    mock_orch_init.return_value = None
    mock_review.return_value = {"approved": True, "feedback": "Good"}
    
    with TestClient(app) as client:
        response = client.post("/api/v1/orchestrator/review", json={
            "instruction": "Do X",
            "deliverables": ["X done"],
            "output": "X is done"
        })
        
        assert response.status_code == 200
        assert response.json()["approved"] is True
