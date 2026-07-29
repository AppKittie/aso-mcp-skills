import sys
import types
import unittest


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

from appkittie_mcp.tools.search_apps import SEARCH_APPS_KEYS, TOOL, _pick


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
            "organicSources",
            "hasInAppPurchases",
            "minInAppPurchaseCount",
            "minInAppPurchasePrice",
            "maxInAppPurchasePrice",
        }

        self.assertLessEqual(expected, properties.keys())


if __name__ == "__main__":
    unittest.main()
