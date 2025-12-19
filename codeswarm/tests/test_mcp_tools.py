import unittest
import os
import shutil
import tempfile
from codeswarm import mcp_tools, config

class TestMcpTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="codeswarm_mcp_test_")
        self.target_project_path = os.path.join(self.test_dir, "mock_root")
        os.makedirs(self.target_project_path, exist_ok=True)

        self.original_project_path = config.DEFAULT_PROJECT_PATH
        config.DEFAULT_PROJECT_PATH = self.target_project_path

    def tearDown(self):
        config.DEFAULT_PROJECT_PATH = self.original_project_path
        shutil.rmtree(self.test_dir)

    def test_local_fs_client(self):
        client = mcp_tools.get_mcp_client("local_fs", "mock://local")
        self.assertIsInstance(client, mcp_tools.LocalFileSystemMcpClient)

        # Test Write
        file_path = os.path.join(self.target_project_path, "test.txt")
        result = client.call_tool("write_file", {"path": file_path, "content": "Hello MCP"})
        self.assertEqual(result["status"], "success")

        # Test Read
        result = client.call_tool("read_file", {"path": file_path})
        self.assertEqual(result["content"], "Hello MCP")

if __name__ == '__main__':
    unittest.main()
