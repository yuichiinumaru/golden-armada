import unittest
from codeswarm.utils.security import resolve_version_range

class TestSecurityUtils(unittest.TestCase):
    def test_resolve_version_range_pypi(self):
        # Basic range checks
        self.assertTrue(resolve_version_range(">=1.0.0", "1.5.0"))
        self.assertTrue(resolve_version_range(">=1.0.0,<2.0.0", "1.5.0"))
        self.assertFalse(resolve_version_range(">=1.0.0,<2.0.0", "2.0.0"))
        self.assertFalse(resolve_version_range(">=1.0.0,<2.0.0", "0.9.9"))

    def test_resolve_version_range_invalid(self):
        # Invalid versions or ranges should return False
        self.assertFalse(resolve_version_range("invalid", "1.0.0"))
        self.assertFalse(resolve_version_range(">=1.0.0", "invalid"))

if __name__ == '__main__':
    unittest.main()
