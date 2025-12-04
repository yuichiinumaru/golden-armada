import unittest
from unittest.mock import MagicMock, patch
from codeswarm.agent_os import AgentOS

class TestKnowledgeAgent(unittest.TestCase):
    @patch('codeswarm.agents.get_knowledge_agent')
    def test_knowledge_retrieval(self, mock_get_knowledge):
        mock_knowledge = MagicMock()
        mock_get_knowledge.return_value = mock_knowledge

        # Simulate retrieval
        mock_response = MagicMock()
        mock_response.content = "Found function X in file Y."
        mock_knowledge.run.return_value = mock_response

        agent = mock_get_knowledge()
        response = agent.run("Find function X")

        self.assertEqual(response.content, "Found function X in file Y.")
        mock_knowledge.run.assert_called_with("Find function X")

if __name__ == '__main__':
    unittest.main()
