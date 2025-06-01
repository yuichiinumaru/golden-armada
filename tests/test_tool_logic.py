import unittest
import os
import shutil
import tempfile
import json
from unittest.mock import patch, MagicMock

# Assuming tool_logic.py is in codeswarm.adk_core
# This import will need to be correct based on the actual PYTHONPATH setup when tests are run.
# If 'codeswarm' is the top-level package and tests are run from the root directory,
# this should work.
from codeswarm.adk_core import tool_logic
# If running `python -m unittest discover tests` from root, this might be an issue
# if codeswarm itself is not directly in PYTHONPATH.
# An alternative, if codeswarm is installed or PYTHONPATH is set up:
# from codeswarm.adk_core import tool_logic

class TestToolLogic(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for the tests
        self.test_dir = tempfile.mkdtemp(prefix="codeswarm_test_")
        # Create a dummy target_project_path within the temp_dir
        # This simulates the root directory of the project being worked on.
        self.target_project_path = os.path.join(self.test_dir, "mock_project_root")
        os.makedirs(self.target_project_path, exist_ok=True)

    def tearDown(self):
        # Remove the temporary directory after the tests
        shutil.rmtree(self.test_dir)

    # --- Test cases for write_file ---
    def test_write_file_create_new(self):
        # Test creating a brand new file.
        file_path = os.path.join(self.target_project_path, "new_file.txt")
        content = "This is a new file."
        result = tool_logic.write_file(file_path, content, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)
        self.assertIn(file_path, result["message"])

    def test_write_file_overwrite_existing(self):
        # Test overwriting an existing file.
        file_path = os.path.join(self.target_project_path, "existing_file.txt")
        initial_content = "Initial content."
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(initial_content)

        new_content = "Overwritten content."
        result = tool_logic.write_file(file_path, new_content, self.target_project_path)
        self.assertEqual(result["status"], "success")
        with open(file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), new_content)

    def test_write_file_create_parent_dirs(self):
        # Test creating necessary parent directories if they don't exist.
        dir_path = os.path.join(self.target_project_path, "parent", "child")
        file_path = os.path.join(dir_path, "nested_file.txt")
        content = "Nested content."
        result = tool_logic.write_file(file_path, content, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)
        self.assertTrue(os.path.isdir(dir_path))

    # Note: Testing for permission errors directly is hard in a portable way.
    # We rely on standard OS behavior and Python's exception handling,
    # which write_file should catch.

    # --- Test cases for read_file ---
    def test_read_file_existing(self):
        file_path = os.path.join(self.target_project_path, "readable_file.txt")
        content = "Content to be read.\nWith multiple lines."
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        result = tool_logic.read_file(file_path, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], content)

    def test_read_file_non_existent(self):
        file_path = os.path.join(self.target_project_path, "non_existent_file.txt")
        result = tool_logic.read_file(file_path, self.target_project_path)
        self.assertEqual(result["status"], "error")
        self.assertIn("File not found", result["message"])
        self.assertIn(file_path, result["message"])

    # --- Test cases for delete_file ---
    def test_delete_file_existing(self):
        file_path = os.path.join(self.target_project_path, "deletable_file.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Delete me.")
        self.assertTrue(os.path.exists(file_path))

        result = tool_logic.delete_file(file_path, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertFalse(os.path.exists(file_path))
        self.assertIn("successfully deleted", result["message"])

    def test_delete_file_non_existent(self):
        file_path = os.path.join(self.target_project_path, "non_existent_to_delete.txt")
        result = tool_logic.delete_file(file_path, self.target_project_path)
        self.assertEqual(result["status"], "error")
        self.assertIn("File not found", result["message"])

    # --- Test cases for list_folder_contents ---
    def test_list_folder_contents_basic(self):
        dir_to_list = os.path.join(self.target_project_path, "list_dir")
        os.makedirs(dir_to_list, exist_ok=True)
        os.makedirs(os.path.join(dir_to_list, "subdir"), exist_ok=True)
        with open(os.path.join(dir_to_list, "file1.txt"), "w", encoding="utf-8") as f:
            f.write("f1")
        with open(os.path.join(dir_to_list, ".hiddenfile"), "w", encoding="utf-8") as f: # Test hidden files
            f.write("hidden")


        result = tool_logic.list_folder_contents(dir_to_list, self.target_project_path)
        self.assertEqual(result["status"], "success")
        # Items should be sorted
        expected_contents = sorted(["subdir/", "file1.txt", ".hiddenfile"])
        self.assertEqual(sorted(result["contents"]), expected_contents)


    def test_list_folder_contents_empty_dir(self):
        empty_dir = os.path.join(self.target_project_path, "empty_list_dir")
        os.makedirs(empty_dir, exist_ok=True)

        result = tool_logic.list_folder_contents(empty_dir, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["contents"], [])

    def test_list_folder_contents_non_existent_dir(self):
        non_existent_dir = os.path.join(self.target_project_path, "no_such_dir_to_list")
        result = tool_logic.list_folder_contents(non_existent_dir, self.target_project_path)
        self.assertEqual(result["status"], "error")
        self.assertIn("Directory not found", result["message"])

    # --- Test cases for search_files_content ---
    def test_search_files_content_found(self):
        search_dir = os.path.join(self.target_project_path, "search_area")
        os.makedirs(search_dir, exist_ok=True)
        file1_path = os.path.join(search_dir, "search1.txt")
        file2_path = os.path.join(search_dir, "search2.py")
        file3_path = os.path.join(search_dir, "search3.txt") # No match

        with open(file1_path, "w", encoding="utf-8") as f:
            f.write("Hello world, this is a test.\nAnother line with Hello query.")
        with open(file2_path, "w", encoding="utf-8") as f:
            f.write("# Python code\ndef hello_world():\n  print('Hello from Python')") # Case-sensitive
        with open(file3_path, "w", encoding="utf-8") as f:
            f.write("Just some other text, no query here.")

        query = "Hello" # Case-sensitive query
        result = tool_logic.search_files_content(search_dir, query, self.target_project_path)
        self.assertEqual(result["status"], "success")

        # Normalize paths for comparison if needed, though here they are constructed similarly
        found_paths = sorted([match["file_path"] for match in result["matches"]])
        expected_paths = sorted([file1_path, file2_path])
        self.assertEqual(found_paths, expected_paths)
        self.assertEqual(len(result["matches"]), 2)

        for match in result["matches"]:
            if match["file_path"] == file1_path:
                self.assertEqual(len(match["lines"]), 2)
                self.assertEqual(match["lines"][0]["line_number"], 1)
                self.assertIn(query, match["lines"][0]["line_content"])
                self.assertEqual(match["lines"][1]["line_number"], 2)
                self.assertIn(query, match["lines"][1]["line_content"])
            elif match["file_path"] == file2_path: # Should match 'Hello from Python'
                self.assertEqual(len(match["lines"]), 1)
                self.assertEqual(match["lines"][0]["line_number"], 3)
                self.assertIn(query, match["lines"][0]["line_content"])


    def test_search_files_content_not_found(self):
        search_dir = os.path.join(self.target_project_path, "search_area_no_match")
        os.makedirs(search_dir, exist_ok=True)
        file1_path = os.path.join(search_dir, "search1.txt")
        with open(file1_path, "w", encoding="utf-8") as f:
            f.write("Some random text, but not the query.")

        query = "NonExistentPattern"
        result = tool_logic.search_files_content(search_dir, query, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["matches"]), 0)
        self.assertTrue(result["message"].startswith("No matches found") or "Search complete. No matches found." in result["message"])


    def test_search_files_content_non_existent_dir(self):
        non_existent_dir = os.path.join(self.target_project_path, "no_such_dir_to_search")
        result = tool_logic.search_files_content(non_existent_dir, "query", self.target_project_path)
        self.assertEqual(result["status"], "error")
        self.assertIn("Directory not found", result["message"])

    # --- Test cases for chunk_file ---
    def test_chunk_file_smaller_than_max(self):
        file_path = os.path.join(self.target_project_path, "small_chunk.txt")
        content = "This is small content, less than 100 chars."
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        result = tool_logic.chunk_file(file_path, max_chunk_size=100, target_project_path=self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["chunks"]), 1)
        self.assertEqual(result["chunks"][0], content)

    def test_chunk_file_larger_than_max(self):
        file_path = os.path.join(self.target_project_path, "large_chunk.txt")
        content = "a" * 150 # 150 'a' characters
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        result = tool_logic.chunk_file(file_path, max_chunk_size=100, target_project_path=self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["chunks"]), 2)
        self.assertEqual(result["chunks"][0], "a" * 100)
        self.assertEqual(result["chunks"][1], "a" * 50)

    def test_chunk_file_empty(self):
        file_path = os.path.join(self.target_project_path, "empty_chunk.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("") # Empty file

        result = tool_logic.chunk_file(file_path, max_chunk_size=100, target_project_path=self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["chunks"]), 1)
        self.assertEqual(result["chunks"][0], "")


    def test_chunk_file_non_existent(self):
        file_path = os.path.join(self.target_project_path, "non_existent_chunk.txt")
        result = tool_logic.chunk_file(file_path, max_chunk_size=100, target_project_path=self.target_project_path)
        self.assertEqual(result["status"], "error")
        self.assertIn("File not found", result["message"])

    # --- Test cases for execute_python_code ---
    def test_execute_python_code_simple_print(self):
        code = "print('Hello from Python')"
        result = tool_logic.execute_python_code(code, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stdout"].strip(), "Hello from Python")
        self.assertEqual(result["stderr"], "") # Expect empty stderr for simple print

    def test_execute_python_code_stderr(self):
        code = "import sys; sys.stderr.write('Error message from Python')"
        result = tool_logic.execute_python_code(code, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["stderr"].strip(), "Error message from Python")


    def test_execute_python_code_exception(self):
        code = "raise ValueError('This is a test value error')"
        result = tool_logic.execute_python_code(code, self.target_project_path)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["stdout"], "")
        self.assertIn("ValueError: This is a test value error", result["stderr"])
        self.assertIn("Traceback (most recent call last):", result["stderr"])
        self.assertEqual(result.get("error_type"), "ValueError") # Check specific error type

    # --- Test cases for execute_shell_command ---
    def test_execute_shell_command_simple_echo(self):
        command = "echo 'Hello from Shell'" # Simple echo command
        result = tool_logic.execute_shell_command(command, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stdout"].strip(), "Hello from Shell")
        self.assertEqual(result["stderr"], "")

    def test_execute_shell_command_stderr(self):
        command = "echo 'Error from Shell' >&2" # Redirect echo to stderr
        result = tool_logic.execute_shell_command(command, self.target_project_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["stderr"].strip(), "Error from Shell")

    def test_execute_shell_command_non_existent(self):
        command = "non_existent_command_ajsdhflakjsdhf" # Highly unlikely to exist
        result = tool_logic.execute_shell_command(command, self.target_project_path)
        self.assertEqual(result["status"], "error")
        self.assertTrue(result["stderr"])
        # Error message varies by OS/shell, so check for common patterns
        self.assertTrue("not found" in result["stderr"].lower() or "no such file" in result["stderr"].lower())


    # --- Test cases for fetch_web_page_text_content ---
    @patch('codeswarm.adk_core.tool_logic.requests.get')
    def test_fetch_web_page_text_content_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simple HTML structure
        mock_response.text = "<html><head><title>Test Page</title></head><body><h1>Header</h1><p>Hello World</p><p>Some other text.</p></body></html>"
        mock_get.return_value = mock_response

        url = "http://fakeexample.com/testpage"
        result = tool_logic.fetch_web_page_text_content(url)

        self.assertEqual(result["status"], "success")
        # Expected text extraction might vary slightly based on BeautifulSoup's parsing
        # Generally, it should concatenate text blocks.
        self.assertIn("Test Page", result["text_content"]) # Title
        self.assertIn("Header", result["text_content"]) # H1
        self.assertIn("Hello World", result["text_content"]) # P
        self.assertIn("Some other text.", result["text_content"]) # P
        self.assertNotIn("<html>", result["text_content"])
        mock_get.assert_called_once_with(url, timeout=10)

    @patch('codeswarm.adk_core.tool_logic.requests.get')
    def test_fetch_web_page_text_content_404_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        # Simulate raise_for_status() behavior for HTTPError
        mock_response.raise_for_status.side_effect = tool_logic.requests.exceptions.HTTPError("404 Client Error: Not Found for url", response=mock_response)
        mock_get.return_value = mock_response

        url = "http://fakeexample.com/notfound"
        result = tool_logic.fetch_web_page_text_content(url)

        self.assertEqual(result["status"], "error")
        self.assertIn("Failed to fetch URL", result["message"])
        self.assertIn("404", result["message"])
        self.assertIn("Not Found", result["message"])
        mock_get.assert_called_once_with(url, timeout=10)

    @patch('codeswarm.adk_core.tool_logic.requests.get')
    def test_fetch_web_page_text_content_connection_error(self, mock_get):
        # Simulate a connection error
        mock_get.side_effect = tool_logic.requests.exceptions.ConnectionError("Connection refused")

        url = "http://fakeexample.com/unreachable"
        result = tool_logic.fetch_web_page_text_content(url)

        self.assertEqual(result["status"], "error")
        self.assertIn("Failed to fetch URL", result["message"])
        self.assertIn("Connection refused", result["message"]) # Check for the specific error
        mock_get.assert_called_once_with(url, timeout=10)

    # --- Test cases for summarize_chunks ---
    def test_summarize_chunks_basic(self):
        chunks = ["This is the first chunk.", "This is the second chunk, slightly longer."]

        mock_summarizer_fn = MagicMock(name="mock_summarizer_fn")
        # Configure side_effect to return a dict that matches expected output structure
        mock_summarizer_fn.side_effect = lambda chunk, tpp, mid: {"status": "success", "summary": f"Summary of '{chunk}'"}

        result = tool_logic.summarize_chunks(chunks, mock_summarizer_fn, self.target_project_path, "test_model_id")

        self.assertEqual(result["status"], "success")
        expected_summary = "Summary of 'This is the first chunk.'\nSummary of 'This is the second chunk, slightly longer.'"
        self.assertEqual(result["full_summary"], expected_summary)

        self.assertEqual(mock_summarizer_fn.call_count, 2)
        mock_summarizer_fn.assert_any_call(chunks[0], self.target_project_path, "test_model_id")
        mock_summarizer_fn.assert_any_call(chunks[1], self.target_project_path, "test_model_id")

    def test_summarize_chunks_empty_list(self):
        chunks = []
        mock_summarizer_fn = MagicMock()
        result = tool_logic.summarize_chunks(chunks, mock_summarizer_fn, self.target_project_path, "test_model_id")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["full_summary"], "") # Empty summary for no chunks
        mock_summarizer_fn.assert_not_called()

    def test_summarize_chunks_one_chunk_fails(self):
        chunks = ["Chunk one is fine.", "Chunk two causes error.", "Chunk three is also fine."]
        mock_summarizer_fn = MagicMock()

        def side_effect_logic(chunk, tpp, mid):
            if "error" in chunk: # Simulate error for a specific chunk
                return {"status": "error", "message": "Simulated summarization error.", "summary": ""}
            return {"status": "success", "summary": f"Summary of '{chunk}'"}
        mock_summarizer_fn.side_effect = side_effect_logic

        result = tool_logic.summarize_chunks(chunks, mock_summarizer_fn, self.target_project_path, "test_model_id")

        # Depending on implementation, this could be 'error' or 'partial_success'
        # Assuming it tries to summarize all and reports errors inline:
        self.assertEqual(result["status"], "partial_success")
        expected_summary = "Summary of 'Chunk one is fine.'\n[Error summarizing chunk: Simulated summarization error.]\nSummary of 'Chunk three is also fine.'"
        self.assertEqual(result["full_summary"], expected_summary)
        self.assertEqual(mock_summarizer_fn.call_count, 3)

if __name__ == '__main__':
    # This allows running the tests directly from the command line
    unittest.main(verbosity=2)
