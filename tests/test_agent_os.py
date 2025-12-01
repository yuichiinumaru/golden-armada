import unittest
from unittest.mock import MagicMock, patch
import json
from codeswarm_agno.agent_os import AgentOS
from codeswarm_agno.models import TaskAssignment, AdminTaskOutput, DevAgentOutput, RevisorAgentOutput

class TestAgentOS(unittest.TestCase):
    @patch('codeswarm_agno.agents.get_admin_agent')
    @patch('codeswarm_agno.agents.get_admin_logger_agent')
    @patch('codeswarm_agno.agents.get_dev_agent')
    @patch('codeswarm_agno.agents.get_revisor_agent')
    def test_run_workflow(self, mock_get_revisor, mock_get_dev, mock_get_logger, mock_get_admin):
        # Mock Admin Agent
        mock_admin = MagicMock()
        mock_get_admin.return_value = mock_admin

        # Mock Admin Output (1 task)
        task = TaskAssignment(
            dev_id=1,
            revisor_id=1,
            file_to_edit_or_create="/tmp/test.py",
            dev_task_description="Write test code",
            revisor_focus_areas="Check syntax"
        )
        admin_output = AdminTaskOutput(tasks=[task])
        mock_admin.run.return_value.content = admin_output

        # Mock Dev Agent
        mock_dev = MagicMock()
        mock_get_dev.return_value = mock_dev
        mock_dev.run.return_value.content = DevAgentOutput(
            status="success",
            message="Done",
            file_path="/tmp/test.py"
        )

        # Mock Revisor Agent
        mock_revisor = MagicMock()
        mock_get_revisor.return_value = mock_revisor
        mock_revisor.run.return_value.content = RevisorAgentOutput(
            status="approved",
            file_path="/tmp/test.py",
            review_comments="Good job",
            approved=True
        )

        # Mock Logger Agent
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_logger.run.return_value.content = MagicMock(status="success", message="Logged")

        # Initialize AgentOS
        os_system = AgentOS(
            goal="Test Goal",
            project_path="/tmp/project",
            pairs=1,
            rounds=1
        )

        # Run
        os_system.run()

        # Verify calls
        mock_admin.run.assert_called()
        mock_dev.run.assert_called()
        mock_revisor.run.assert_called()
        mock_logger.run.assert_called()

        # Verify Tree State
        self.assertEqual(len(os_system.tree.root.children), 1)
        self.assertEqual(os_system.tree.root.children[0].status, "approved")

if __name__ == '__main__':
    unittest.main()
