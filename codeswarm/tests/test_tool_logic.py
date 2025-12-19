import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from codeswarm import tools
from codeswarm import config

class TestToolLogic(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for the tests
        self.test_dir = tempfile.mkdtemp(prefix="codeswarm_test_")
        # Create a dummy target_project_path within the temp_dir
        self.target_project_path = os.path.join(self.test_dir, "mock_project_root")
        os.makedirs(self.target_project_path, exist_ok=True)

        # Override the DEFAULT_PROJECT_PATH in config for the duration of the tests
        self.original_project_path = config.DEFAULT_PROJECT_PATH
        config.DEFAULT_PROJECT_PATH = self.target_project_path

    def tearDown(self):
        # Restore original config
        config.DEFAULT_PROJECT_PATH = self.original_project_path
        # Remove the temporary directory after the tests
        shutil.rmtree(self.test_dir)

    # --- Test cases for write_file ---
    def test_write_file_create_new(self):
        file_path = os.path.join(self.target_project_path, "new_file.txt")
        content = "This is a new file."
        result = tools.write_file(file_path, content)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)

    def test_write_file_outside_project(self):
        # Test security check
        file_path = os.path.join(self.test_dir, "outside.txt")
        result = tools.write_file(file_path, "hack")
        self.assertEqual(result["status"], "error")
        self.assertIn("Access denied", result["message"])

    def test_write_file_overwrite_existing(self):
        file_path = os.path.join(self.target_project_path, "existing_file.txt")
        initial_content = "Initial content."
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(initial_content)

        new_content = "Overwritten content."
        result = tools.write_file(file_path, new_content)
        self.assertEqual(result["status"], "success")
        with open(file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), new_content)

    def test_write_file_create_parent_dirs(self):
        dir_path = os.path.join(self.target_project_path, "parent", "child")
        file_path = os.path.join(dir_path, "nested_file.txt")
        content = "Nested content."
        result = tools.write_file(file_path, content)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)

    # --- Test cases for read_file ---
    def test_read_file_existing(self):
        file_path = os.path.join(self.target_project_path, "readable_file.txt")
        content = "Content to be read.\nWith multiple lines."
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        result = tools.read_file(file_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], content)

    def test_read_file_non_existent(self):
        file_path = os.path.join(self.target_project_path, "non_existent_file.txt")
        result = tools.read_file(file_path)
        self.assertEqual(result["status"], "error")
        self.assertTrue(isinstance(result["message"], str))

    # --- Test cases for delete_file ---
    def test_delete_file_existing(self):
        file_path = os.path.join(self.target_project_path, "deletable_file.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Delete me.")
        self.assertTrue(os.path.exists(file_path))

        result = tools.delete_file(file_path)
        self.assertEqual(result["status"], "success")
        self.assertFalse(os.path.exists(file_path))

    def test_delete_file_non_existent(self):
        file_path = os.path.join(self.target_project_path, "non_existent_to_delete.txt")
        result = tools.delete_file(file_path)
        self.assertEqual(result["status"], "error")

    # --- Test cases for list_folder_contents ---
    def test_list_folder_contents_basic(self):
        dir_to_list = os.path.join(self.target_project_path, "list_dir")
        os.makedirs(dir_to_list, exist_ok=True)
        os.makedirs(os.path.join(dir_to_list, "subdir"), exist_ok=True)
        with open(os.path.join(dir_to_list, "file1.txt"), "w", encoding="utf-8") as f:
            f.write("f1")

        result = tools.list_folder_contents(dir_to_list)
        self.assertEqual(result["status"], "success")
        expected_contents = sorted(["subdir", "file1.txt"])
        self.assertEqual(sorted(result["content"]), expected_contents)

    def test_list_folder_contents_non_existent_dir(self):
        non_existent_dir = os.path.join(self.target_project_path, "no_such_dir")
        result = tools.list_folder_contents(non_existent_dir)
        self.assertEqual(result["status"], "error")

    # --- Test cases for search_files_content ---
    def test_search_files_content_found(self):
        search_dir = os.path.join(self.target_project_path, "search_area")
        os.makedirs(search_dir, exist_ok=True)
        file1_path = os.path.join(search_dir, "search1.txt")
        with open(file1_path, "w", encoding="utf-8") as f:
            f.write("Hello world")

        result = tools.search_files_content(search_dir, "Hello")
        self.assertEqual(result["status"], "success")
        self.assertIn(file1_path, result["content"])

    # --- Test cases for chunk_file ---
    def test_chunk_file(self):
        file_path = os.path.join(self.target_project_path, "chunks.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("a" * 150)

        result = tools.chunk_file(file_path, max_chunk_size=100)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["content"]), 2)

    # --- Test cases for execute_python_code ---
    def test_execute_python_code_simple_print(self):
        code = "print('Hello from Python')"
        result = tools.execute_python_code(code)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stdout"].strip(), "Hello from Python")

    def test_execute_python_code_exception(self):
        code = "raise ValueError('Test Error')"
        result = tools.execute_python_code(code)
        # subprocess.run returns success even if the script failed, unless check=True
        # Our tool implementation catches Exception but subprocess.run doesn't raise unless timeout/etc
        # It returns stdout/stderr.
        self.assertEqual(result["status"], "success")
        self.assertIn("ValueError: Test Error", result["stderr"])

    # --- Test cases for execute_shell_command ---
    def test_execute_shell_command_simple_echo(self):
        command = "echo 'Hello from Shell'"
        result = tools.execute_shell_command(command)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stdout"].strip(), "Hello from Shell")

    # --- Test cases for fetch_web_page_text_content ---
    @patch('codeswarm.tools.requests.get')
    def test_fetch_web_page_text_content_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>Hello World</p></body></html>"
        mock_get.return_value = mock_response

        result = tools.fetch_web_page_text_content("http://example.com")
        self.assertEqual(result["status"], "success")
        self.assertIn("Hello World", result["content"])

    # --- Test cases for summarize_chunks ---
    def test_summarize_chunks(self):
        # The current tools.summarize_chunks just returns the chunks for the agent to summarize
        chunks = ["chunk1", "chunk2"]
        result = tools.summarize_chunks(chunks)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["prepared_chunks"], chunks)

if __name__ == '__main__':
    unittest.main(verbosity=2)
