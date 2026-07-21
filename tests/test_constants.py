import unittest

from appkittie_mcp.constants import API_BASE


class ApiBaseTests(unittest.TestCase):
    def test_api_base_uses_canonical_host_without_redirect(self):
        self.assertEqual(API_BASE, "https://www.appkittie.com")


if __name__ == "__main__":
    unittest.main()
