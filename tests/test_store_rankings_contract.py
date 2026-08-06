import asyncio
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch


# The production MCP runs in Pyodide. These tests only exercise Python request
# construction, so lightweight bridge stand-ins are sufficient.
js = types.ModuleType("js")
js.Headers = object
js.fetch = object
sys.modules.setdefault("js", js)
pyodide = types.ModuleType("pyodide")
pyodide_ffi = types.ModuleType("pyodide.ffi")
pyodide_ffi.to_js = lambda value, **_kwargs: value
sys.modules.setdefault("pyodide", pyodide)
sys.modules.setdefault("pyodide.ffi", pyodide_ffi)

from appkittie_mcp.tools import get_store_ranking_history, list_store_rankings


class StoreRankingsContractTests(unittest.TestCase):
    def test_tool_schemas_expose_chart_identity(self):
        list_properties = list_store_rankings.TOOL["inputSchema"]["properties"]
        history_schema = get_store_ranking_history.TOOL["inputSchema"]

        self.assertLessEqual(
            {"source", "collection", "country", "category", "limit", "offset"},
            list_properties.keys(),
        )
        self.assertIn("category", history_schema["required"])
        self.assertEqual(
            history_schema["properties"]["days"]["maximum"],
            365,
        )

    def test_list_tool_forwards_filters(self):
        args = {
            "source": "apple_mobile",
            "collection": "TOP_FREE",
            "country": "US",
            "category": "BUSINESS",
            "limit": 10,
        }
        api_get = AsyncMock(return_value=({"data": []}, None))

        with patch.object(list_store_rankings, "api_get", api_get):
            asyncio.run(list_store_rankings.handle(args, "test-key"))

        api_get.assert_awaited_once_with("/api/v1/trending", args, "test-key")

    def test_history_tool_escapes_slug_and_forwards_series_filters(self):
        args = {
            "appSlug": "app/example",
            "source": "apple_mobile",
            "collection": "TOP_FREE",
            "country": "US",
            "category": "BUSINESS",
            "days": 30,
        }
        api_get = AsyncMock(return_value=({"data": {}}, None))

        with patch.object(get_store_ranking_history, "api_get", api_get):
            asyncio.run(get_store_ranking_history.handle(args, "test-key"))

        api_get.assert_awaited_once_with(
            "/api/v1/trending/app%2Fexample/history",
            {
                "source": "apple_mobile",
                "collection": "TOP_FREE",
                "country": "US",
                "category": "BUSINESS",
                "days": 30,
            },
            "test-key",
        )


if __name__ == "__main__":
    unittest.main()
