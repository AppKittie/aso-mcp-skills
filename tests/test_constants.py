import unittest

from appkittie_mcp.constants import AD_SORT_BY_OPTIONS, API_BASE


class ApiBaseTests(unittest.TestCase):
    def test_api_base_uses_canonical_host_without_redirect(self):
        self.assertEqual(API_BASE, "https://www.appkittie.com")

    def test_ad_sort_options_include_meta_spend_and_reach_periods(self):
        for period in ("7d", "30d", "90d"):
            self.assertIn(
                f"app_meta_ads_estimated_spend_{period}_usd",
                AD_SORT_BY_OPTIONS,
            )
            self.assertIn(
                f"app_meta_ads_estimated_reach_{period}",
                AD_SORT_BY_OPTIONS,
            )


if __name__ == "__main__":
    unittest.main()
