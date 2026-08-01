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

from appkittie_mcp.tools import app_scoped
from appkittie_mcp.tools.list_organic_content import (
    ORGANIC_FILTER_KEYS,
    ORGANIC_FILTER_PROPERTIES,
    TOOL,
    handle,
)


class ListOrganicContentContractTests(unittest.IsolatedAsyncioTestCase):
    def test_schema_and_forwarded_filter_keys_stay_in_sync(self):
        properties = TOOL["inputSchema"]["properties"]

        self.assertEqual(ORGANIC_FILTER_KEYS, tuple(ORGANIC_FILTER_PROPERTIES))
        self.assertLessEqual(ORGANIC_FILTER_PROPERTIES.keys(), properties.keys())
        self.assertNotIn("anyOf", TOOL["inputSchema"])

    def test_exposes_dashboard_filter_groups(self):
        properties = TOOL["inputSchema"]["properties"]
        expected = {
            "search",
            "textSearchFields",
            "categories",
            "excludedCategories",
            "contentSources",
            "excludedContentSources",
            "contentLanguages",
            "excludedContentLanguages",
            "minFollowers",
            "maxFollowers",
            "minViews",
            "maxViews",
            "minAppDownloads",
            "maxAppDownloads",
            "minAppRevenue",
            "maxAppRevenue",
            "sortBy",
            "sortOrder",
        }

        self.assertLessEqual(expected, properties.keys())
        self.assertTrue(
            {
                "mediaTypes",
                "excludedMediaTypes",
                "minCarouselCount",
                "maxCarouselCount",
                "hasVideo",
                "hasCarousel",
                "minComments",
                "maxComments",
                "minShares",
                "maxShares",
                "minSaves",
                "maxSaves",
                "minEngagement",
                "maxEngagement",
            }.isdisjoint(properties)
        )

    async def test_global_filters_are_forwarded_to_the_rest_api(self):
        args = {
            "search": "fitness",
            "categories": ["Health & Fitness", "Lifestyle"],
            "contentLanguages": ["EN"],
            "minFollowers": 10_000,
            "sortBy": "view_count",
            "sortOrder": "desc",
            "limit": 5,
        }
        response = {"data": [], "pagination": {"totalCount": 0}}

        with patch.object(
            app_scoped, "api_get", new=AsyncMock(return_value=(response, None))
        ) as api_get:
            result = await handle(args, "test-key")

        api_get.assert_awaited_once_with(
            "/api/v1/organic",
            {
                "count": 5,
                "search": "fitness",
                "categories": ["Health & Fitness", "Lifestyle"],
                "contentLanguages": ["EN"],
                "minFollowers": 10_000,
                "sortBy": "view_count",
                "sortOrder": "desc",
            },
            "test-key",
        )
        self.assertFalse(result.get("isError", False))
        self.assertEqual(json.loads(result["content"][0]["text"]), response)


if __name__ == "__main__":
    unittest.main()
