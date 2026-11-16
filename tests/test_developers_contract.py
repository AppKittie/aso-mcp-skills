import json
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch
from urllib.parse import quote


# Production uses Pyodide; these contract tests only construct requests.
js = types.ModuleType("js")
js.Headers = object
js.fetch = object
sys.modules.setdefault("js", js)
sys.modules.setdefault("pyodide", types.ModuleType("pyodide"))
ffi = types.ModuleType("pyodide.ffi")
ffi.to_js = lambda value, **_kwargs: value
sys.modules.setdefault("pyodide.ffi", ffi)

from appkittie_mcp.api import _clean_params
from appkittie_mcp.tools import TOOLS, TOOL_HANDLERS, get_developer_detail, search_developers


class DevelopersContractTests(unittest.IsolatedAsyncioTestCase):
    def test_tools_are_registered_and_expose_the_api_filters(self):
        self.assertIn("search_developers", TOOL_HANDLERS)
        self.assertIn("get_developer_detail", TOOL_HANDLERS)
        self.assertEqual(len({tool["name"] for tool in TOOLS}), len(TOOLS))
        self.assertEqual(get_developer_detail.TOOL["inputSchema"]["required"], ["name"])
        self.assertEqual(set(search_developers.TOOL["inputSchema"]["properties"]), {
            "search", "stores", "categories", "excludedCategories", "minApps", "maxApps",
            "minMrr", "maxMrr", "minDownloads", "maxDownloads", "hasWebsite",
            "latestReleasedAfter", "latestReleasedBefore", "sortBy", "sortOrder", "limit", "cursor",
        })

    async def test_search_forwards_filters_and_preserves_pagination(self):
        args = {
            "search": "Games", "stores": "both", "categories": ["Games", "Education"],
            "excludedCategories": ["Business"], "minApps": 2, "maxApps": 20,
            "minMrr": 10, "maxMrr": 1000, "minDownloads": 0, "maxDownloads": 50000,
            "hasWebsite": False, "latestReleasedAfter": 1700000000, "latestReleasedBefore": 1800000000,
            "sortBy": "total_mrr", "sortOrder": "desc", "limit": 5, "cursor": 10,
        }
        response = {"data": [{"developer": "Example Games"}], "pagination": {"nextCursor": 15, "totalCount": 100}}
        with patch.object(search_developers, "api_get", new=AsyncMock(return_value=(response, None))) as api:
            result = await TOOL_HANDLERS["search_developers"]({**args, "unknown": "ignored"}, "test-key")
        api.assert_awaited_once_with("/api/v1/developers", args, "test-key")
        self.assertEqual(json.loads(result["content"][0]["text"]), response)
        self.assertEqual(_clean_params(args)["hasWebsite"], "false")
        self.assertEqual(_clean_params(args)["categories"], "Games,Education")

    async def test_detail_encodes_exact_names_and_preserves_portfolio(self):
        name = 'Example / Games & "Co" + 日本'
        response = {"data": {"developer": name, "summary": {"appCount": 1}, "apps": [{"app_slug": "example"}]}}
        with patch.object(get_developer_detail, "api_get", new=AsyncMock(return_value=(response, None))) as api:
            result = await TOOL_HANDLERS["get_developer_detail"]({"name": name}, "test-key")
        api.assert_awaited_once_with(f"/api/v1/developers/{quote(name, safe='')}", {}, "test-key")
        self.assertEqual(json.loads(result["content"][0]["text"]), response)

    async def test_detail_rejects_invalid_names_without_calling_the_api(self):
        for name in (None, "", " ", 123, "x" * 1025):
            with self.subTest(name=name), patch.object(get_developer_detail, "api_get", new_callable=AsyncMock) as api:
                result = await get_developer_detail.handle({"name": name}, "test-key")
                self.assertTrue(result["isError"])
                api.assert_not_awaited()

    async def test_both_tools_surface_api_errors(self):
        for module, args in ((search_developers, {}), (get_developer_detail, {"name": "Unknown"})):
            with self.subTest(tool=module.TOOL["name"]), patch.object(module, "api_get", new=AsyncMock(return_value=(None, "HTTP 402: Insufficient credits"))):
                result = await module.handle(args, "test-key")
                self.assertTrue(result["isError"])
                self.assertIn("Insufficient credits", result["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
