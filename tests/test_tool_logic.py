import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import requests # For requests.exceptions

from codeswarm.adk_core import tool_logic

class TestToolLogic(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.environ["TARGET_PROJECT_PATH_FOR_TOOLS"] = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if "TARGET_PROJECT_PATH_FOR_TOOLS" in os.environ:
            del os.environ["TARGET_PROJECT_PATH_FOR_TOOLS"]

    def test_create_file_success(self):
        file_path = os.path.join(self.test_dir, "test_create.txt")
        content = "Hello from create_file!"
        result = tool_logic.create_file(file_path, content)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), content)

    def test_read_file_success(self):
        file_path = os.path.join(self.test_dir, "test_read.txt")
        content = "Hello, world!"
        with open(file_path, "w") as f: f.write(content)
        result = tool_logic.read_file(file_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], content)

    def test_read_file_not_found(self):
        file_path = os.path.join(self.test_dir, "non_existent_file.txt")
        result = tool_logic.read_file(file_path)
        self.assertEqual(result["status"], "error")
        self.assertIn("No such file or directory", result["message"])

    def test_update_file_success(self):
        file_path = os.path.join(self.test_dir, "test_update.txt")
        initial_content = "Initial content."
        updated_content = "Updated content."
        with open(file_path, "w") as f: f.write(initial_content)
        result = tool_logic.update_file(file_path, updated_content)
        self.assertEqual(result["status"], "success")
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), updated_content)

    def test_delete_file_success(self):
        file_path = os.path.join(self.test_dir, "test_delete.txt")
        with open(file_path, "w") as f: f.write("Delete me.")
        self.assertTrue(os.path.exists(file_path))
        result = tool_logic.delete_file(file_path)
        self.assertEqual(result["status"], "success")
        self.assertFalse(os.path.exists(file_path))

    def test_delete_file_not_found(self):
        file_path = os.path.join(self.test_dir, "non_existent_to_delete.txt")
        result = tool_logic.delete_file(file_path)
        self.assertEqual(result["status"], "error")

    def test_write_file_success_absolute_path(self):
        file_path = os.path.join(self.test_dir, "test_write_abs.txt")
        content = "Absolute write."
        result = tool_logic.write_file(file_path, content)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), content)

    def test_write_file_success_relative_path_resolution(self):
        relative_file_path = "test_write_rel.txt"
        full_expected_path = os.path.join(self.test_dir, relative_file_path)
        content = "Relative write resolved."
        result = tool_logic.write_file(relative_file_path, content)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(full_expected_path))
        with open(full_expected_path, "r") as f:
            self.assertEqual(f.read(), content)

    def test_write_file_subfolder_creation(self):
        relative_file_path = os.path.join("sub", "test_write_subfolder.txt")
        full_expected_path = os.path.join(self.test_dir, relative_file_path)
        content = "Subfolder write."
        result = tool_logic.write_file(relative_file_path, content)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(full_expected_path))
        with open(full_expected_path, "r") as f:
            self.assertEqual(f.read(), content)

    def test_write_file_no_env_var_relative_path(self):
        original_env_var = os.environ.pop("TARGET_PROJECT_PATH_FOR_TOOLS", None)
        relative_file_path = "test_write_rel_no_env.txt"
        content = "Relative write no env."
        result = tool_logic.write_file(relative_file_path, content) # Should write to CWD
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(relative_file_path)) # Check in CWD
        with open(relative_file_path, "r") as f:
            self.assertEqual(f.read(), content)
        os.remove(relative_file_path)
        if original_env_var is not None:
            os.environ["TARGET_PROJECT_PATH_FOR_TOOLS"] = original_env_var
        else: # ensure it's set back to test_dir for other tests if it wasn't there before
             os.environ["TARGET_PROJECT_PATH_FOR_TOOLS"] = self.test_dir

    def test_list_folder_contents_success(self):
        os.makedirs(os.path.join(self.test_dir, "subdir1"))
        with open(os.path.join(self.test_dir, "file1.txt"), "w") as f: f.write("")
        with open(os.path.join(self.test_dir, "file2.txt"), "w") as f: f.write("")
        result = tool_logic.list_folder_contents(self.test_dir)
        self.assertEqual(result["status"], "success")
        self.assertIsInstance(result["content"], list)
        self.assertCountEqual(result["content"], ["subdir1", "file1.txt", "file2.txt"])

    def test_list_folder_contents_empty(self):
        empty_subdir = os.path.join(self.test_dir, "empty_subdir")
        os.makedirs(empty_subdir)
        result = tool_logic.list_folder_contents(empty_subdir)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], [])

    def test_list_folder_contents_not_found(self):
        result = tool_logic.list_folder_contents(os.path.join(self.test_dir, "non_existent_subdir"))
        self.assertEqual(result["status"], "error")

    def test_search_files_content_success(self):
        file1_path = os.path.join(self.test_dir, "search_file1.txt")
        file2_path = os.path.join(self.test_dir, "search_file2.txt") # Does not contain the keyword
        subdir_path = os.path.join(self.test_dir, "search_subdir")
        os.makedirs(subdir_path)
        file3_path = os.path.join(subdir_path, "search_file3.txt")

        with open(file1_path, "w") as f: f.write("Hello keyword here.")
        with open(file2_path, "w") as f: f.write("No match for the search term.") # Explicitly no "keyword"
        with open(file3_path, "w") as f: f.write("Another keyword in subdir.")

        result = tool_logic.search_files_content(self.test_dir, "keyword")
        self.assertEqual(result["status"], "success")
        self.assertIsInstance(result["content"], list)

        normalized_content = sorted([os.path.normpath(p) for p in result["content"]])
        # Corrected expectation: only files containing "keyword"
        expected_paths = sorted([os.path.normpath(file1_path), os.path.normpath(file3_path)])
        self.assertEqual(normalized_content, expected_paths)

    def test_search_files_content_no_results(self):
        file1_path = os.path.join(self.test_dir, "search_no_res1.txt")
        with open(file1_path, "w") as f: f.write("Some content.")
        result = tool_logic.search_files_content(self.test_dir, "nonexistentquery")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], [])

    def test_search_files_content_target_dir_not_exists(self):
        result = tool_logic.search_files_content(os.path.join(self.test_dir, "non_existent_search_dir"), "query")
        self.assertEqual(result["status"], "error")
        self.assertIn("Directory not found", result["message"])

    @patch('codeswarm.adk_core.tool_logic.requests.get')
    def test_fetch_web_page_text_content_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><head><title>Test</title></head><body><p>Hello World</p><span>Some more text</span></body></html>"
        mock_get.return_value = mock_response
        result = tool_logic.fetch_web_page_text_content("http://example.com")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "Test Hello World Some more text")
        mock_get.assert_called_once_with("http://example.com", timeout=10)

    @patch('codeswarm.adk_core.tool_logic.requests.get')
    def test_fetch_web_page_text_content_failure_status_code(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_get.return_value = mock_response
        result = tool_logic.fetch_web_page_text_content("http://example.com/notfound")
        self.assertEqual(result["status"], "error")
        self.assertIn("404 Client Error", result["message"])

    @patch('codeswarm.adk_core.tool_logic.requests.get')
    def test_fetch_web_page_text_content_failure_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        result = tool_logic.fetch_web_page_text_content("http://example.com/failed")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Connection error")

    def test_chunk_file_success(self):
        file_path = os.path.join(self.test_dir, "chunk_test.txt")
        content = "a" * 5000
        with open(file_path, "w") as f: f.write(content)
        result = tool_logic.chunk_file(file_path, max_chunk_size=2000)
        self.assertEqual(result["status"], "success")
        self.assertIsInstance(result["content"], list)
        self.assertEqual(len(result["content"]), 3)
        self.assertEqual(result["content"][0], "a" * 2000)
        self.assertEqual(result["content"][1], "a" * 2000)
        self.assertEqual(result["content"][2], "a" * 1000)

    def test_chunk_file_small_file(self):
        file_path = os.path.join(self.test_dir, "chunk_small.txt")
        content = "abc"
        with open(file_path, "w") as f: f.write(content)
        result = tool_logic.chunk_file(file_path, max_chunk_size=100)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["content"]), 1)
        self.assertEqual(result["content"][0], content)

    def test_chunk_file_not_found(self):
        result = tool_logic.chunk_file(os.path.join(self.test_dir, "chunk_not_found.txt"))
        self.assertEqual(result["status"], "error")

    def test_summarize_chunks_success(self):
        chunks = ["This is chunk one.", "This is chunk two.", "And a third one."]
        mock_summarizer_fn = MagicMock(side_effect=lambda x: f"Summary of '{x}'")
        result = tool_logic.summarize_chunks(chunks, mock_summarizer_fn)
        self.assertEqual(result["status"], "success")
        expected_summary = "Summary of 'This is chunk one.'\nSummary of 'This is chunk two.'\nSummary of 'And a third one.'"
        self.assertEqual(result["content"], expected_summary)
        self.assertEqual(mock_summarizer_fn.call_count, 3)

    def test_summarize_chunks_empty_list(self):
        result = tool_logic.summarize_chunks([], MagicMock())
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "")

    def test_summarize_chunks_summarizer_error(self):
        chunks = ["This is chunk one."]
        mock_summarizer_fn = MagicMock(side_effect=Exception("Summarizer failed"))
        result = tool_logic.summarize_chunks(chunks, mock_summarizer_fn)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Summarizer failed")

if __name__ == '__main__':
    unittest.main()
