import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import time
import os

from codeswarm import khala_integration

class TestKhalaIntegration(unittest.TestCase):
    def setUp(self):
        # Reset singleton
        khala_integration.KhalaSystem._instance = None
        pass

    def tearDown(self):
        khala_integration.stop_khala_background()
        # Wait for thread to cleanup?
        time.sleep(1)

    @patch('codeswarm.khala_integration.SurrealDBClient')
    @patch('codeswarm.khala_integration.CacheManager')
    def test_search_tool(self, MockCache, MockSurreal):
        # Setup mocks
        mock_client = MockSurreal.return_value
        mock_client.initialize = AsyncMock()
        mock_client.close = AsyncMock()
        mock_client.search_memories_by_bm25 = AsyncMock(return_value=[
            {"content": "Found memory 1", "score": 0.9},
            {"content": "Found memory 2", "score": 0.8}
        ])

        mock_cache = MockCache.return_value
        mock_cache.start = AsyncMock()
        mock_cache.stop = AsyncMock()

        # Force reload or reset if needed
        khala_integration.KhalaSystem._instance = None

        # Start system
        khala_integration.start_khala_background()

        # Give background thread time to start and run start()
        time.sleep(2)

        # Get tool
        tools = khala_integration.get_khala_tools()
        self.assertTrue(len(tools) > 0, "Should have tools")
        search_tool = tools[0]

        # Run tool
        result = search_tool("query")

        # Verify
        print(f"Result: {result}")
        self.assertIn("Found memory 1", result)
        self.assertIn("Found memory 2", result)

        # Verify calls
        mock_client.initialize.assert_called()
        # Note: search might not be called if start failed, but result would indicate error.
        if "Search failed" in result:
            self.fail(f"Search failed: {result}")

        mock_client.search_memories_by_bm25.assert_called()

if __name__ == "__main__":
    unittest.main()
