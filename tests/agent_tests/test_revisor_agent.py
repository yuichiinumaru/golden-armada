import unittest
import asyncio
import json
import tempfile
import shutil
import os # For GOOGLE_API_KEY check
from pathlib import Path

from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

# Assuming 'codeswarm' is in the Python path or its structure allows these imports
from codeswarm.adk_agents import create_revisor_llm_agent
from codeswarm.adk_models import RevisorAgentOutput
from codeswarm.adk_core.adk_setup import get_runner
from codeswarm.adk_core import tool_logic # For write_file

# This script assumes that the necessary environment variables (like GOOGLE_API_KEY)
# are set for the LlmAgent to initialize and run.

class TestRevisorAgent(unittest.TestCase):
    tmp_dir_obj = None
    tmp_dir = None
    target_project_path = None
    target_project_path_str = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir_obj = tempfile.TemporaryDirectory(prefix="cs_revisor_test_")
        cls.tmp_dir = cls.tmp_dir_obj.name
        cls.target_project_path = Path(cls.tmp_dir) / "test_project"
        cls.target_project_path.mkdir(parents=True, exist_ok=True)
        cls.target_project_path_str = str(cls.target_project_path)
        print(f"Temporary project path created: {cls.target_project_path_str}")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'tmp_dir_obj'):
            cls.tmp_dir_obj.cleanup()
            print(f"Temporary project path removed: {cls.target_project_path_str}")

    async def run_agent_test(self, agent, input_dict):
        session_service = InMemorySessionService()
        runner = get_runner(session_service=session_service)

        session_id = await session_service.create_session()
        session = await session_service.get_session(session_id=session_id)

        input_json = json.dumps(input_dict)
        message = Content(parts=[Part(text=input_json)])

        print(f"\n--- Running RevisorAgent with input: ---\n{json.dumps(input_dict, indent=2)}")

        final_response_text = None
        error_occurred = False

        async for event in runner.run_async(
            agent_id=agent.id, session=session, request_body=message
        ):
            if event.type == "agent_response" and event.is_last_event:
                if event.response and event.response.parts:
                    final_response_text = event.response.parts[0].text
                break
            elif event.type == "error":
                print(f"ERROR event in agent execution: {event.error_details}")
                final_response_text = json.dumps({
                    "status": "error_in_agent",
                    "message": str(event.error_details),
                    "file_path": input_dict.get("file_to_review", ""),
                    "review_comments": "Error during agent execution.",
                    "approved": False
                })
                error_occurred = True
                break

        if final_response_text is None and not error_occurred:
             final_response_text = json.dumps({
                "status": "error_no_response",
                "message": "Agent did not produce a final response text.",
                "file_path": input_dict.get("file_to_review", ""),
                "review_comments": "No response from agent.",
                "approved": False
            })

        print(f"--- RevisorAgent raw output: ---\n{final_response_text}")
        return final_response_text

    async def test_revisor_agent_approve_code_async(self):
        print("\n>>> Starting test_revisor_agent_approve_code_async")
        revisor_agent = create_revisor_llm_agent(revisor_id=1)

        file_to_review_name = "dummy_code_correct.py"
        file_to_review_path = str(self.target_project_path / file_to_review_name)
        correct_code_content = "def add(a, b):\n    return a + b\n\n# Test function\nif __name__ == '__main__':\n    print(f'2 + 3 = {add(2,3)}')\n"

        write_result = tool_logic.write_file(file_to_review_path, correct_code_content, self.target_project_path_str)
        self.assertEqual(write_result["status"], "success", "Setup: Failed to write dummy_code_correct.py")

        revisor_input_dict = {
            "file_to_review": file_to_review_path,
            "focus_areas": "Check for basic correctness, readability, and simple test coverage.",
            "target_project_path": self.target_project_path_str,
            "dev_task_description": "A simple function to add two numbers, with a basic self-test."
        }

        final_response_text = await self.run_agent_test(revisor_agent, revisor_input_dict)
        self.assertIsNotNone(final_response_text, "Agent did not produce any response text.")

        try:
            parsed_output = RevisorAgentOutput.model_validate_json(final_response_text)
            print(f"--- RevisorAgent parsed approval output: ---\n{parsed_output.model_dump_json(indent=2)}")
        except Exception as e:
            self.fail(f"Failed to parse RevisorAgent output: {e}\nRaw output was: {final_response_text}")

        self.assertIsInstance(parsed_output, RevisorAgentOutput)
        self.assertEqual(Path(parsed_output.file_path).resolve(), Path(file_to_review_path).resolve(), "Output file_path does not match input.")
        self.assertTrue(parsed_output.approved, f"Code should have been approved. Comments: {parsed_output.review_comments}. Raw: {final_response_text}")
        self.assertEqual(parsed_output.status, "success", f"Status should be 'success' for approved code. Comments: {parsed_output.review_comments}")
        print("<<< Finished test_revisor_agent_approve_code_async: PASSED")

    async def test_revisor_agent_request_changes_async(self):
        print("\n>>> Starting test_revisor_agent_request_changes_async")
        revisor_agent = create_revisor_llm_agent(revisor_id=2)

        file_to_review_name = "dummy_code_flawed.py"
        file_to_review_path = str(self.target_project_path / file_to_review_name)
        flawed_code_content = "def multiply(a, b):\n    # Intended to multiply, but uses addition\n    return a + b\n\n# Test function\nif __name__ == '__main__':\n    print(f'2 * 3 = {multiply(2,3)}') # Expected 6, will get 5\n"

        write_result = tool_logic.write_file(file_to_review_path, flawed_code_content, self.target_project_path_str)
        self.assertEqual(write_result["status"], "success", "Setup: Failed to write dummy_code_flawed.py")

        revisor_input_dict = {
            "file_to_review": file_to_review_path,
            "focus_areas": "Verify the correctness of the multiplication logic and the self-test.",
            "target_project_path": self.target_project_path_str,
            "dev_task_description": "A function to multiply two numbers, including a self-test."
        }

        final_response_text = await self.run_agent_test(revisor_agent, revisor_input_dict)
        self.assertIsNotNone(final_response_text, "Agent did not produce any response text for flawed code.")

        try:
            parsed_output = RevisorAgentOutput.model_validate_json(final_response_text)
            print(f"--- RevisorAgent parsed changes request output: ---\n{parsed_output.model_dump_json(indent=2)}")
        except Exception as e:
            self.fail(f"Failed to parse RevisorAgent output for flawed code: {e}\nRaw output was: {final_response_text}")

        self.assertIsInstance(parsed_output, RevisorAgentOutput)
        self.assertEqual(Path(parsed_output.file_path).resolve(), Path(file_to_review_path).resolve(), "Output file_path does not match input for flawed code.")
        self.assertFalse(parsed_output.approved, f"Code should NOT have been approved due to flaw. Comments: {parsed_output.review_comments}. Raw: {final_response_text}")
        self.assertEqual(parsed_output.status, "requires_changes", f"Status should be 'requires_changes'. Comments: {parsed_output.review_comments}")
        self.assertTrue(len(parsed_output.review_comments) > 10, "Review comments should be provided for flawed code and be somewhat descriptive.")
        # Optionally, check for keywords if the LLM is consistent enough:
        # self.assertIn("add", parsed_output.review_comments.lower(), "Review comments should mention the addition error.")
        # self.assertIn("multiply", parsed_output.review_comments.lower(), "Review comments should mention multiplication.")
        print("<<< Finished test_revisor_agent_request_changes_async: PASSED")

async def main_test_runner():
    TestRevisorAgent.setUpClass()
    test_instance = TestRevisorAgent()
    try:
        await test_instance.test_revisor_agent_approve_code_async()
        await test_instance.test_revisor_agent_request_changes_async()
        print("\nAll RevisorAgent async tests completed.")
    except Exception as e:
        print(f"An error occurred during RevisorAgent test execution: {e}")
        raise
    finally:
        TestRevisorAgent.tearDownClass()

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("CRITICAL ERROR: GOOGLE_API_KEY environment variable is not set.")
        print("Skipping RevisorAgent tests as they require API access.")
    else:
        try:
            asyncio.run(main_test_runner())
        except Exception as e:
            print(f"Test run failed with exception: {e}")
            exit(1)
