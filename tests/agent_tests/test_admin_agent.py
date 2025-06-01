import unittest
import asyncio
import json
import tempfile
import shutil
import os # Added for os.getenv
from pathlib import Path

from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
# pydantic.BaseModel is imported by adk_models, so not strictly needed here if only using those.

# Assuming 'codeswarm' is in the Python path or its structure allows these imports
from codeswarm.adk_agents import create_admin_llm_agent
from codeswarm.adk_models import AdminTaskOutput, AdminLogUpdateOutput
from codeswarm.adk_core.adk_setup import get_runner
from codeswarm.adk_core import tool_logic # Added for file operations

# This script assumes that the necessary environment variables (like GOOGLE_API_KEY)
# are set for the LlmAgent to initialize and run.

class TestAdminAgent(unittest.TestCase):
    tmp_dir = None
    target_project_path_str = None # Will be string representation of Path

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir_obj = tempfile.TemporaryDirectory(prefix="cs_admin_test_")
        cls.tmp_dir = cls.tmp_dir_obj.name # Get the string path
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
        # Using default InMemorySessionService and default runner from adk_setup
        session_service = InMemorySessionService()
        runner = get_runner(session_service=session_service)

        session_id = await session_service.create_session()
        session = await session_service.get_session(session_id=session_id)

        input_json = json.dumps(input_dict)
        message = Content(parts=[Part(text=input_json)])

        print(f"\n--- Running AdminAgent with input: ---\n{json.dumps(input_dict, indent=2)}")

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
                # Synthesize an error JSON that Pydantic models can try to parse
                final_response_text = json.dumps({"status": "error", "message": str(event.error_details), "tasks": [], "approved": False, "review_comments": "", "file_path": ""})
                error_occurred = True
                break

        if final_response_text is None and not error_occurred:
             final_response_text = json.dumps({"status": "error", "message": "Agent did not produce a final response text."})


        print(f"--- AdminAgent raw output: ---\n{final_response_text}")
        return final_response_text

    async def test_admin_task_assignment_async(self):
        print("\n>>> Starting test_admin_task_assignment_async")
        # Create a new agent instance for each test to ensure isolation if needed,
        # though create_admin_llm_agent should be idempotent for same params.
        admin_agent = create_admin_llm_agent()

        admin_input_dict = {
            "overall_project_goal": "Create a simple calculator command line application in Python that can add, subtract, multiply, and divide.",
            "target_project_path": self.target_project_path_str,
            "round": 1,
            "previous_summaries": [],
            "current_phase": "task_assignment"
        }

        final_response_text = await self.run_agent_test(admin_agent, admin_input_dict)
        self.assertIsNotNone(final_response_text, "Agent did not produce any response text.")

        try:
            parsed_output = AdminTaskOutput.model_validate_json(final_response_text)
            print(f"--- AdminAgent parsed task assignment output: ---\n{parsed_output.model_dump_json(indent=2)}")
        except Exception as e:
            self.fail(f"Failed to parse AdminAgent task assignment output: {e}\nRaw output was: {final_response_text}")

        self.assertIsInstance(parsed_output, AdminTaskOutput)
        # For a valid goal, it should generate at least one task.
        self.assertTrue(len(parsed_output.tasks) > 0, f"AdminAgent should generate at least one task. Got: {parsed_output.tasks}")

        for task in parsed_output.tasks:
            self.assertTrue(hasattr(task, "dev_id"), "Task missing dev_id")
            self.assertTrue(hasattr(task, "revisor_id"), "Task missing revisor_id")
            self.assertIsNotNone(task.file_to_edit_or_create, "Task file_to_edit_or_create is None")
            self.assertTrue(task.file_to_edit_or_create, "Task file_to_edit_or_create is empty") # Must not be empty
            self.assertTrue(hasattr(task, "dev_task_description"), "Task missing dev_task_description")
            self.assertTrue(hasattr(task, "revisor_focus_areas"), "Task missing revisor_focus_areas")

            # Path validation
            self.assertTrue(
                Path(task.file_to_edit_or_create).is_absolute(),
                f"Task file_to_edit_or_create '{task.file_to_edit_or_create}' is not an absolute path."
            )
            self.assertTrue(
                task.file_to_edit_or_create.startswith(self.target_project_path_str),
                f"Task file_to_edit_or_create '{task.file_to_edit_or_create}' does not start with target_project_path '{self.target_project_path_str}'"
            )
        print("<<< Finished test_admin_task_assignment_async: PASSED (structural checks)")

    async def test_admin_logging_async(self):
        print("\n>>> Starting test_admin_logging_async")
        admin_agent = create_admin_llm_agent()

        sample_file_path = str(Path(self.target_project_path_str) / "calculator" / "main.py")

        admin_input_dict = {
            "dev_outputs": [{"dev_id": 1, "output": {"status": "success", "message": "Implemented calculator.add", "file_path": sample_file_path}}],
            "revisor_feedback": [{"revisor_id": 1, "output": {"status": "success", "file_path": sample_file_path, "review_comments": "LGTM", "approved": True}}],
            "target_project_path": self.target_project_path_str,
            "round": 1,
            "current_phase": "logging_and_updates"
        }

        final_response_text = await self.run_agent_test(admin_agent, admin_input_dict)
        self.assertIsNotNone(final_response_text, "Agent did not produce any response text for logging phase.")

        try:
            parsed_output = AdminLogUpdateOutput.model_validate_json(final_response_text)
            print(f"--- AdminAgent parsed logging output: ---\n{parsed_output.model_dump_json(indent=2)}")
        except Exception as e:
            self.fail(f"Failed to parse AdminAgent logging output: {e}\nRaw output was: {final_response_text}")

        self.assertIsInstance(parsed_output, AdminLogUpdateOutput)
        # The agent is prompted to use tools like 'write_file' which should return success.
        # The agent's own final response should then also indicate success for the logging operation.
        self.assertEqual(parsed_output.status, "success", f"AdminAgent logging status was not 'success'. Message: '{parsed_output.message}'. Raw: {final_response_text}")
        print("<<< Finished test_admin_logging_async: PASSED (structural checks)")

    async def test_admin_log_file_updates_async(self):
        print("\n>>> Starting test_admin_log_file_updates_async")
        admin_agent = create_admin_llm_agent()

        docs_dir = Path(self.target_project_path_str) / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        changelog_path = docs_dir / "changelog.log"
        tasklist_path = docs_dir / "tasklist.md"

        initial_changelog_content = "INITIAL_CHANGELOG_CONTENT - Should be overwritten."
        initial_tasklist_content = "INITIAL_TASKLIST_CONTENT - Should be overwritten."

        self.assertEqual(tool_logic.write_file(str(changelog_path), initial_changelog_content, self.target_project_path_str)["status"], "success")
        self.assertEqual(tool_logic.write_file(str(tasklist_path), initial_tasklist_content, self.target_project_path_str)["status"], "success")

        # Give some distinct info for the agent to log
        dev_output_file = Path(self.target_project_path_str) / "module" / "feature_x.py"
        dev_output_file.parent.mkdir(parents=True, exist_ok=True) # Ensure parent dir exists for the dummy path

        admin_input_dict = {
            "dev_outputs": [{"dev_id": 1, "output": {"status": "success", "message": "Implemented amazing feature X in module/feature_x.py", "file_path": str(dev_output_file)}}],
            "revisor_feedback": [{"revisor_id": 1, "output": {"status": "success", "file_path": str(dev_output_file), "review_comments": "Feature X looks absolutely fantastic, approved!", "approved": True}}],
            "target_project_path": self.target_project_path_str,
            "round": 1,
            "current_phase": "logging_and_updates"
        }

        final_response_text = await self.run_agent_test(admin_agent, admin_input_dict)
        self.assertIsNotNone(final_response_text, "Agent did not produce a final response text for log file update test.")

        try:
            parsed_agent_output = AdminLogUpdateOutput.model_validate_json(final_response_text)
        except Exception as e:
            self.fail(f"Failed to parse AdminAgent output for log file update test: {e}\nRaw output was: {final_response_text}")

        self.assertEqual(parsed_agent_output.status, "success", f"AdminAgent status was not 'success' for log file update. Message: {parsed_agent_output.message}")

        # Verify changelog.log modification
        changelog_read_result = tool_logic.read_file(str(changelog_path), self.target_project_path_str)
        self.assertEqual(changelog_read_result["status"], "success", "Failed to read changelog.log after agent run.")
        self.assertNotEqual(changelog_read_result["content"], initial_changelog_content, "changelog.log content was not modified.")
        self.assertTrue(len(changelog_read_result["content"].strip()) > 0, "changelog.log is empty after agent run.")
        self.assertIn("feature X", changelog_read_result["content"], "Changelog does not seem to contain expected info from dev_outputs.")


        # Verify tasklist.md modification
        tasklist_read_result = tool_logic.read_file(str(tasklist_path), self.target_project_path_str)
        self.assertEqual(tasklist_read_result["status"], "success", "Failed to read tasklist.md after agent run.")
        self.assertNotEqual(tasklist_read_result["content"], initial_tasklist_content, "tasklist.md content was not modified.")
        self.assertTrue(len(tasklist_read_result["content"].strip()) > 0, "tasklist.md is empty after agent run.")
        # Tasklist content is more dynamic, checking for non-emptiness and change is a good start.
        # A more robust test might check for specific markers if the prompt for tasklist generation is very specific.

        print("<<< Finished test_admin_log_file_updates_async: PASSED (file modification checks)")


async def main_test_runner():
    # This function will be called by asyncio.run()
    # We need to manage the test class instance and its class-level setup/teardown.

    TestAdminAgent.setUpClass() # Call @classmethod setup

    test_instance = TestAdminAgent() # Create an instance to run tests

    try:
        await test_instance.test_admin_task_assignment_async()
        await test_instance.test_admin_logging_async()
        await test_instance.test_admin_log_file_updates_async() # Added new test
        print("\nAll AdminAgent async tests completed.")
    except Exception as e:
        print(f"An error occurred during test execution: {e}")
        raise # Re-raise to ensure test runner sees it as a failure
    finally:
        TestAdminAgent.tearDownClass() # Call @classmethod teardown

if __name__ == "__main__":
    # This approach allows running async tests defined in a unittest.TestCase structure.
    # For more complex scenarios or integration with standard test runners like 'pytest',
    # you might use 'pytest-asyncio'.
    # This script expects to be run directly, e.g., `python -m tests.agent_tests.test_admin_agent`
    # Ensure PYTHONPATH is set up correctly if codeswarm is not installed.
    # Example: PYTHONPATH=$PYTHONPATH:$(pwd) python tests/agent_tests/test_admin_agent.py

    # Check if GOOGLE_API_KEY is set, as it's crucial for LLM agent tests
    # This os.getenv requires 'import os' at the top of the file.
    if not os.getenv("GOOGLE_API_KEY"):
        print("CRITICAL ERROR: GOOGLE_API_KEY environment variable is not set.")
        print("Skipping AdminAgent tests as they require API access.")
    else:
        try:
            asyncio.run(main_test_runner())
        except Exception as e:
            print(f"Test run failed with exception: {e}")
            # Exit with a non-zero code to indicate failure in CI environments
            exit(1)
