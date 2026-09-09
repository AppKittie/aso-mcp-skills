import sys
import types
import unittest
from unittest.mock import AsyncMock, patch


# Production uses the Pyodide bridge; contract tests need no network access.
js = types.ModuleType("js")
js.Headers = object
js.fetch = object
sys.modules.setdefault("js", js)
sys.modules.setdefault("pyodide", types.ModuleType("pyodide"))
ffi = types.ModuleType("pyodide.ffi")
ffi.to_js = lambda value, **_kwargs: value
sys.modules.setdefault("pyodide.ffi", ffi)

from appkittie_mcp.tools import TOOLS, TOOL_HANDLERS
from appkittie_mcp.tools import app_scoped, get_app_historicals, get_app_reviews, get_store_ranking_history


class ToolSchemaCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    def test_all_advertised_tools_have_client_compatible_root_schemas(self):
        # Claude rejects the entire request if any tool has a root combinator.
        for tool in TOOLS:
            with self.subTest(tool=tool["name"]):
                schema = tool["inputSchema"]
                self.assertEqual(schema.get("type"), "object")
                self.assertTrue({"oneOf", "allOf", "anyOf"}.isdisjoint(schema))
                self.assertIn("properties", schema)

    async def test_missing_scope_is_rejected_before_api_calls(self):
        cases = [
            ("get_app_historicals", get_app_historicals, "api_get_app_resource", {}),
            ("get_app_reviews", get_app_reviews, "api_post", {}),
            ("get_store_ranking_history", get_store_ranking_history, "api_get", {"category": "BUSINESS"}),
            ("list_creators", app_scoped, "api_get", {}),
        ]
        for name, module, api_function, args in cases:
            with self.subTest(tool=name):
                with patch.object(module, api_function, new_callable=AsyncMock) as api:
                    result = await TOOL_HANDLERS[name](args, "test-key")
                self.assertTrue(result.get("isError"))
                api.assert_not_awaited()

    async def test_creators_still_accept_category_or_identifier_aliases(self):
        for key in ("category", "appSlug", "app_slug", "appId", "appStoreId", "appStoreUrl"):
            with self.subTest(key=key):
                with patch.object(app_scoped, "api_get", new=AsyncMock(return_value=({}, None))) as api:
                    result = await TOOL_HANDLERS["list_creators"]({key: "example"}, "test-key")
                self.assertFalse(result.get("isError", False))
                api.assert_awaited_once_with("/api/v1/creators", {key: "example"}, "test-key")
