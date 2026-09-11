import sys
import types
import unittest
from unittest.mock import AsyncMock, patch


# The MCP runs in Pyodide, where the `js` bridge is available. Contract tests
# only inspect static tool metadata, so lightweight stand-ins are sufficient.
js = types.ModuleType("js")
js.Headers = object
js.fetch = object
sys.modules.setdefault("js", js)
pyodide = types.ModuleType("pyodide")
pyodide_ffi = types.ModuleType("pyodide.ffi")
pyodide_ffi.to_js = lambda value, **_kwargs: value
sys.modules.setdefault("pyodide", pyodide)
sys.modules.setdefault("pyodide.ffi", pyodide_ffi)

from appkittie_mcp.api import _clean_params
from appkittie_mcp.tools.search_apps import SEARCH_APPS_KEYS, TOOL, _pick, handle


class SearchAppsContractTests(unittest.TestCase):
    def test_forwarded_parameters_are_derived_from_tool_schema(self):
        schema_keys = tuple(TOOL["inputSchema"]["properties"])

        self.assertEqual(SEARCH_APPS_KEYS, schema_keys)
        self.assertEqual(
            _pick({key: key for key in schema_keys}, SEARCH_APPS_KEYS),
            {key: key for key in schema_keys},
        )

    def test_search_apps_exposes_current_api_filter_groups(self):
        properties = TOOL["inputSchema"]["properties"]
        expected = {
            "countries",
            "excludedCountries",
            "releasedBefore",
            "updatedBefore",
            "textSearchFields",
            "hasIpadSupport",
            "hasWebFunnel",
            "organicSources",
            "hasMetaAdSpend",
            "minMetaAdSpend",
            "maxMetaAdSpend",
            "hasInAppPurchases",
            "minInAppPurchaseCount",
            "minInAppPurchasePrice",
            "maxInAppPurchasePrice",
        }

        self.assertLessEqual(expected, properties.keys())


class SearchAppsWebFunnelTests(unittest.IsolatedAsyncioTestCase):
    async def test_web_funnel_is_forwarded_and_serialized_without_dropping_false(self):
        self.assertEqual(
            TOOL["inputSchema"]["properties"]["hasWebFunnel"]["type"], "boolean"
        )
        for args, expected in [
            ({"hasWebFunnel": True}, {"hasWebFunnel": "true"}),
            ({"hasWebFunnel": False}, {"hasWebFunnel": "false"}),
            ({}, {}),
        ]:
            with self.subTest(args=args), patch(
                "appkittie_mcp.tools.search_apps.api_get",
                new_callable=AsyncMock,
                return_value=({"data": []}, None),
            ) as api_get:
                await handle(args, "test-key")
                api_get.assert_awaited_once_with("/api/v1/apps", args, "test-key")
                self.assertEqual(_clean_params(api_get.call_args.args[1]), expected)


if __name__ == "__main__":
    unittest.main()
