import unittest
from unittest.mock import MagicMock, patch
import json
import os
from codeswarm.agent_os import AgentOS
from codeswarm.models import (
    TaskAssignment, AdminTaskOutput, DevAgentOutput, RevisorAgentOutput, AdminLogUpdateOutput
)

class MockResponse:
    def __init__(self, content):
        self.content = content

def mock_admin_run(*args, **kwargs):
    # Return a single task
    task = TaskAssignment(
        dev_id=1,
        revisor_id=1,
        file_to_edit_or_create=os.path.abspath("test_project_output/hello.py"),
        dev_task_description="Create a hello world script",
        revisor_focus_areas="Check for prints"
    )
    output = AdminTaskOutput(tasks=[task])
    return MockResponse(output)

def mock_dev_run(*args, **kwargs):
    output = DevAgentOutput(
        status="success",
        message="Created file",
        file_path=os.path.abspath("test_project_output/hello.py")
    )
    return MockResponse(output)

def mock_revisor_run(*args, **kwargs):
    output = RevisorAgentOutput(
        status="success",
        file_path=os.path.abspath("test_project_output/hello.py"),
        review_comments="Looks good",
        approved=True
    )
    return MockResponse(output)

def mock_logger_run(*args, **kwargs):
    output = AdminLogUpdateOutput(
        status="success",
        message="Logs updated"
    )
    return MockResponse(output)

def mock_planner_run(*args, **kwargs):
    return MockResponse("Strategic Plan: Build hello world.")

def mock_knowledge_run(*args, **kwargs):
    return MockResponse("Context: Use python print function.")

class TestAgentOS(unittest.TestCase):
    @patch('codeswarm.agents.get_admin_agent')
    @patch('codeswarm.agents.get_dev_agent')
    @patch('codeswarm.agents.get_revisor_agent')
    @patch('codeswarm.agents.get_admin_logger_agent')
    @patch('codeswarm.agents.get_planner_agent')
    @patch('codeswarm.agents.get_knowledge_agent')
    def test_run_flow(self, mock_get_knowledge, mock_get_planner, mock_get_logger, mock_get_revisor, mock_get_dev, mock_get_admin):
        # Setup mocks
        admin_agent = MagicMock()
        admin_agent.run.side_effect = mock_admin_run
        mock_get_admin.return_value = admin_agent

        dev_agent = MagicMock()
        dev_agent.run.side_effect = mock_dev_run
        mock_get_dev.return_value = dev_agent

        revisor_agent = MagicMock()
        revisor_agent.run.side_effect = mock_revisor_run
        mock_get_revisor.return_value = revisor_agent

        logger_agent = MagicMock()
        logger_agent.run.side_effect = mock_logger_run
        mock_get_logger.return_value = logger_agent

        planner_agent = MagicMock()
        planner_agent.run.side_effect = mock_planner_run
        mock_get_planner.return_value = planner_agent

        knowledge_agent = MagicMock()
        knowledge_agent.run.side_effect = mock_knowledge_run
        mock_get_knowledge.return_value = knowledge_agent

        # Create a temp dir for project path to ensure state saving works
        import tempfile
        import shutil
        test_dir = tempfile.mkdtemp(prefix="codeswarm_flow_test_")

        try:
            # Run AgentOS
            agent_os = AgentOS(
                goal="Test Goal",
                project_path=test_dir,
                pairs=1,
                rounds=1
            )

            agent_os.run()
        finally:
            shutil.rmtree(test_dir)

        # Assertions
        # Admin called once per round (1 round)
        admin_agent.run.assert_called()
        self.assertEqual(admin_agent.run.call_count, 1)

        # Dev called once (1 task)
        dev_agent.run.assert_called()
        self.assertEqual(dev_agent.run.call_count, 1)

        # Revisor called once
        revisor_agent.run.assert_called()
        self.assertEqual(revisor_agent.run.call_count, 1)

        # Logger called once
        logger_agent.run.assert_called()
        self.assertEqual(logger_agent.run.call_count, 1)

if __name__ == '__main__':
    unittest.main()
