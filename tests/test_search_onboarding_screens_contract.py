import json
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch


js = types.ModuleType("js")
js.Headers = object
js.fetch = object
sys.modules.setdefault("js", js)
pyodide = types.ModuleType("pyodide")
pyodide_ffi = types.ModuleType("pyodide.ffi")
pyodide_ffi.to_js = lambda value, **_kwargs: value
sys.modules.setdefault("pyodide", pyodide)
sys.modules.setdefault("pyodide.ffi", pyodide_ffi)

from appkittie_mcp.tools import search_onboarding_screens


class SearchOnboardingScreensContractTests(unittest.IsolatedAsyncioTestCase):
    def test_schema_matches_api_contract(self):
        properties = search_onboarding_screens.TOOL["inputSchema"]["properties"]

        self.assertEqual(properties["limit"]["default"], 50)
        self.assertEqual(properties["limit"]["maximum"], 100)
        self.assertEqual(
            properties["label"]["enum"],
            [
                "onboarding", "quiz", "paywall", "home", "permissions",
                "feature_intro", "profile_setup", "welcome", "content",
                "preferences", "other", "sign_up", "settings", "login",
                "success", "subscription", "discount", "lesson", "search",
                "checkout",
            ],
        )

    async def test_handler_forwards_filters_and_returns_api_response(self):
        args = {
            "label": "paywall",
            "appSlug": "app-example",
            "categories": ["Health & Fitness"],
            "limit": 3,
            "cursor": 6,
        }
        response = {
            "data": [
                {
                    "app_slug": "app-example",
                    "title": "Example",
                    "url": "https://example.com",
                    "onboarding_images": ["https://example.com/paywall.jpg"],
                }
            ],
            "pagination": {"nextCursor": 7, "totalCount": 1},
        }

        with patch.object(
            search_onboarding_screens,
            "api_get",
            new=AsyncMock(return_value=(response, None)),
        ) as api_get:
            result = await search_onboarding_screens.handle(args, "test-key")

        api_get.assert_awaited_once_with(
            "/api/v1/onboarding/screens", args, "test-key"
        )
        self.assertFalse(result.get("isError", False))
        self.assertEqual(json.loads(result["content"][0]["text"]), response)


if __name__ == "__main__":
    unittest.main()
