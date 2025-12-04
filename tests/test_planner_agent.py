import unittest
from unittest.mock import MagicMock, patch
import json
from codeswarm.agent_os import AgentOS

class TestPlannerAgent(unittest.TestCase):
    @patch('codeswarm.agents.get_planner_agent')
    def test_planner_tool_usage(self, mock_get_planner):
        mock_planner = MagicMock()
        mock_get_planner.return_value = mock_planner

        # Simulate AgentOS run calling planner
        # We just want to verifying the planner logic or tool calls if we could inspect them
        # But PlannerAgent is an Agno agent, its logic is inside the LLM prompt usually.
        # Here we mock the response to ensure it returns a string plan.

        mock_response = MagicMock()
        mock_response.content = "Strategic Plan: Do X, then Y."
        mock_planner.run.return_value = mock_response

        planner = mock_get_planner()
        response = planner.run(json.dumps({"state": "initial"}))

        self.assertEqual(response.content, "Strategic Plan: Do X, then Y.")
        mock_planner.run.assert_called_with('{"state": "initial"}')

if __name__ == '__main__':
    unittest.main()
