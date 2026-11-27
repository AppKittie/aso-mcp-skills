import re
import unittest

from appkittie_mcp.constants import AD_SORT_BY_OPTIONS, API_BASE
from appkittie_mcp.prompts import render_prompt


class ApiBaseTests(unittest.TestCase):
    def test_ad_intelligence_selects_the_requested_networks(self):
        for platform, filters, creative_sources in [
            ("google", ["hasGoogleAds: true"], ["google"]),
            ("tiktok", ["hasTikTokAds: true"], ["tiktok"]),
            ("meta", ["adsSource: 'meta'"], ["meta"]),
            ("apple", ["hasAppleAds: true"], []),
            ("all", ["adsSource: 'all'", "hasAppleAds: true"], ["meta", "tiktok", "google"]),
            ("both", ["adsSource: 'meta'", "hasTikTokAds: true", "hasAppleAds: true"], ["meta", "tiktok"]),
        ]:
            with self.subTest(platform=platform):
                messages = render_prompt("ad_intelligence", {"category_or_search": "fitness", "ad_platform": platform})
                text = messages[0]["content"]["text"]
                self.assertEqual(re.findall(r"search: 'fitness', (.*?), sortBy", text), filters)
                self.assertEqual(re.findall(r"adSource: '([a-z]+)'", text), creative_sources)
                self.assertEqual("get_ad_detail" in text, bool(creative_sources))

    def test_ad_intelligence_defaults_to_all_and_accepts_legacy_named_arguments(self):
        args = {"category_or_search": "fitness"}
        messages = render_prompt("ad_intelligence", args)
        self.assertEqual(messages, render_prompt("ad_intelligence", {**args, "ad_platform": "all"}))
        self.assertEqual(messages, render_prompt("ad_intelligence", [{"name": "category_or_search", "value": "fitness"}]))

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
