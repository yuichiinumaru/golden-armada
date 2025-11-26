import unittest
import asyncio
from unittest.mock import patch, MagicMock

from codeswarm.main_adk_controller import main_async

class TestOrchestratorWorkflow(unittest.TestCase):
    @patch('argparse.ArgumentParser')
    @patch('codeswarm.main_adk_controller.get_runner')
    def test_main_async_runs_without_error(self, mock_get_runner, mock_parser):
        """
        Test that the main_async function can be run without raising an exception.
        """
        mock_args = MagicMock()
        mock_args.path = 'test_project'
        mock_args.goal = 'test goal'
        mock_args.pairs = 1
        mock_args.rounds = 1
        mock_args.debug = False
        mock_args.session_id = None
        mock_args.model = None
        mock_args.resume = False
        mock_args.list_sessions = False
        mock_parser.return_value.parse_args.return_value = mock_args

        mock_runner = MagicMock()
        async def mock_run_async(*args, **kwargs):
            yield MagicMock(is_final_response=lambda: True, content=MagicMock(parts=[MagicMock(text="Workflow finished.")]))
        mock_runner.run_async = mock_run_async
        mock_get_runner.return_value = mock_runner

        try:
            asyncio.run(main_async())
        except Exception as e:
            self.fail(f"main_async raised an exception: {e}")

    @patch('argparse.ArgumentParser')
    @patch('codeswarm.main_adk_controller.create_codeswarm_workflow')
    def test_workflow_is_called_with_correct_parameters(self, mock_create_workflow, mock_parser):
        """
        Test that the create_codeswarm_workflow function is called with the correct
        number of pairs, rounds, and model override from the command line arguments.
        """
        mock_args = MagicMock()
        mock_args.path = 'test_project'
        mock_args.goal = 'test goal'
        mock_args.pairs = 2
        mock_args.rounds = 3
        mock_args.debug = False
        mock_args.session_id = None
        mock_args.model = 'test-model'
        mock_args.resume = False
        mock_args.list_sessions = False
        mock_parser.return_value.parse_args.return_value = mock_args

        with patch('codeswarm.main_adk_controller.get_runner'):
            asyncio.run(main_async())

        mock_create_workflow.assert_called_once_with(pairs=2, rounds=3, model_override='test-model')

if __name__ == '__main__':
    unittest.main()