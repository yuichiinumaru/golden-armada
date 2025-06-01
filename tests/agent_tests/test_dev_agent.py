import unittest
import asyncio
import json
import tempfile
import shutil
import os # For GOOGLE_API_KEY check
from pathlib import Path
import sys # For mocking
from unittest.mock import MagicMock # For mocking

# --- Mocking google.adk.sessions before actual import ---
MOCK_ADK_MODULES = [
    "google.adk",
    "google.adk.sessions",
]
for mod_name in MOCK_ADK_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

# Ensure InMemorySessionService is a mock if google.adk.sessions was mocked
if isinstance(sys.modules.get("google.adk.sessions"), MagicMock):
    sys.modules["google.adk.sessions"].InMemorySessionService = MagicMock()
# --- End Mocking ---

from google.adk.sessions import InMemorySessionService
from google.generativeai.types import Content, Part # Corrected import path

# Assuming 'codeswarm' is in the Python path or its structure allows these imports
from codeswarm.adk_agents import create_dev_llm_agent
from codeswarm.adk_models import DevAgentOutput
from codeswarm.adk_core.adk_setup import get_runner
from codeswarm.adk_core import tool_logic # For read_file, write_file

# This script assumes that the necessary environment variables (like GOOGLE_API_KEY)
# are set for the LlmAgent to initialize and run.

class TestDevAgent(unittest.TestCase):
    tmp_dir_obj = None
    tmp_dir = None
    target_project_path = None
    target_project_path_str = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir_obj = tempfile.TemporaryDirectory(prefix="cs_dev_test_")
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

        user_id = "test_user_dev" # Consistent user_id
        session_id = await session_service.create_session(user_id=user_id) # Pass user_id if create_session supports it
        # session = await session_service.get_session(user_id=user_id, session_id=session_id)

        input_json = json.dumps(input_dict)
        message = Content(parts=[Part(text=input_json)])

        print(f"\n--- Running DevAgent with input: ---\n{json.dumps(input_dict, indent=2)}")

        final_response_text = None
        error_occurred = False

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
            agent_id=agent.id
        ):
            if event.type == "agent_response" and event.is_last_event:
                if event.response and event.response.parts:
                    final_response_text = event.response.parts[0].text
                break
            elif event.type == "error":
                print(f"ERROR event in agent execution: {event.error_details}")
                final_response_text = json.dumps({"status": "error", "message": str(event.error_details), "file_path": input_dict.get("file_to_edit_or_create", "")})
                error_occurred = True
                break

        if final_response_text is None and not error_occurred:
             final_response_text = json.dumps({"status": "error", "message": "Agent did not produce a final response text.", "file_path": input_dict.get("file_to_edit_or_create", "")})

        print(f"--- DevAgent raw output: ---\n{final_response_text}")
        return final_response_text

    async def test_dev_agent_file_creation_async(self):
        print("\n>>> Starting test_dev_agent_file_creation_async")
        dev_agent = create_dev_llm_agent(dev_id=1)

        file_to_create_name = "new_hello.py"
        file_to_create_path = str(self.target_project_path / file_to_create_name)

        dev_input_dict = {
            "dev_task_description": "Create a new Python file that contains only one line: print('Hello, World!')",
            "file_to_edit_or_create": file_to_create_path,
            "target_project_path": self.target_project_path_str
        }

        final_response_text = await self.run_agent_test(dev_agent, dev_input_dict)
        self.assertIsNotNone(final_response_text, "Agent did not produce any response text.")

        try:
            parsed_output = DevAgentOutput.model_validate_json(final_response_text)
            print(f"--- DevAgent parsed file creation output: ---\n{parsed_output.model_dump_json(indent=2)}")
        except Exception as e:
            self.fail(f"Failed to parse DevAgent output: {e}\nRaw output was: {final_response_text}")

        self.assertIsInstance(parsed_output, DevAgentOutput)
        self.assertEqual(parsed_output.status, "success", f"DevAgent status was not 'success'. Message: {parsed_output.message}. Raw: {final_response_text}")
        self.assertEqual(Path(parsed_output.file_path).resolve(), Path(file_to_create_path).resolve(), "Output file_path does not match input.")

        # Verify file creation and content
        read_result = tool_logic.read_file(file_to_create_path)
        self.assertEqual(read_result["status"], "success", f"Failed to read the file '{file_to_create_path}' supposedly created by DevAgent.")
        self.assertIn("print('Hello, World!')", read_result["content"], "File content incorrect.")
        # Ensure it *only* contains the print statement as per strict instruction
        self.assertEqual(read_result["content"].strip(), "print('Hello, World!')", "File content has extra data.")
        print("<<< Finished test_dev_agent_file_creation_async: PASSED")

    async def test_dev_agent_file_modification_async(self):
        print("\n>>> Starting test_dev_agent_file_modification_async")
        dev_agent = create_dev_llm_agent(dev_id=2) # Use a different ID for clarity if logs were combined

        file_to_modify_name = "existing_code.py"
        file_to_modify_path = str(self.target_project_path / file_to_modify_name)
        initial_content = "def existing_function():\n    pass\n"

        # Pre-create the file using tool_logic
        write_setup_result = tool_logic.write_file(file_to_modify_path, initial_content)
        self.assertEqual(write_setup_result["status"], "success", "Setup: Failed to write initial file for modification test.")

        dev_input_dict = {
            "dev_task_description": "Append the line '# Modified by DevAgent' at the end of the existing Python file.",
            "file_to_edit_or_create": file_to_modify_path,
            "target_project_path": self.target_project_path_str
        }

        final_response_text = await self.run_agent_test(dev_agent, dev_input_dict)
        self.assertIsNotNone(final_response_text, "Agent did not produce any response text for modification.")

        try:
            parsed_output = DevAgentOutput.model_validate_json(final_response_text)
            print(f"--- DevAgent parsed file modification output: ---\n{parsed_output.model_dump_json(indent=2)}")
        except Exception as e:
            self.fail(f"Failed to parse DevAgent output for modification: {e}\nRaw output was: {final_response_text}")

        self.assertIsInstance(parsed_output, DevAgentOutput)
        self.assertEqual(parsed_output.status, "success", f"DevAgent status was not 'success' for modification. Message: {parsed_output.message}. Raw: {final_response_text}")
        self.assertEqual(Path(parsed_output.file_path).resolve(), Path(file_to_modify_path).resolve(), "Output file_path does not match input for modification.")

        # Verify file modification
        read_result = tool_logic.read_file(file_to_modify_path)
        self.assertEqual(read_result["status"], "success", f"Failed to read the file '{file_to_modify_path}' supposedly modified by DevAgent.")

        expected_content_lines = initial_content.splitlines()
        expected_content_lines.append("# Modified by DevAgent")
        # Allow for trailing newline flexibility
        self.assertIn(initial_content.strip(), read_result["content"].strip(), "Initial content missing after modification.")
        self.assertIn("# Modified by DevAgent", read_result["content"], "Appended line missing after modification.")
        self.assertEqual(read_result["content"].strip(), "\n".join(expected_content_lines).strip())

        print("<<< Finished test_dev_agent_file_modification_async: PASSED")


async def main_test_runner():
    TestDevAgent.setUpClass()
    test_instance = TestDevAgent()
    try:
        await test_instance.test_dev_agent_file_creation_async()
        await test_instance.test_dev_agent_file_modification_async()
        print("\nAll DevAgent async tests completed.")
    except Exception as e:
        print(f"An error occurred during DevAgent test execution: {e}")
        raise
    finally:
        TestDevAgent.tearDownClass()

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("CRITICAL ERROR: GOOGLE_API_KEY environment variable is not set.")
        print("Skipping DevAgent tests as they require API access.")
    else:
        try:
            asyncio.run(main_test_runner())
        except Exception as e:
            print(f"Test run failed with exception: {e}")
            exit(1)
