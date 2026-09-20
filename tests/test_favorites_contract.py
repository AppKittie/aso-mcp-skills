import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

js = types.ModuleType("js")
js.Headers = object
js.fetch = object
sys.modules.setdefault("js", js)
sys.modules.setdefault("pyodide", types.ModuleType("pyodide"))
ffi = types.ModuleType("pyodide.ffi")
ffi.to_js = lambda value, **_kwargs: value
sys.modules.setdefault("pyodide.ffi", ffi)

from appkittie_mcp.api import _clean_params
from appkittie_mcp.tools import TOOL_HANDLERS, TOOLS
from appkittie_mcp.tools import list_favorite_apps, search_apps


class FavoritesContractTests(unittest.IsolatedAsyncioTestCase):
    def test_favorites_tool_is_read_only_and_no_mutation_is_registered(self):
        self.assertIn(list_favorite_apps.TOOL, TOOLS)
        self.assertIs(TOOL_HANDLERS["list_favorite_apps"], list_favorite_apps.handle)
        self.assertTrue(list_favorite_apps.TOOL["annotations"]["readOnlyHint"])
        self.assertNotIn("set_app_favorite", TOOL_HANDLERS)

    async def test_general_search_has_no_favorites_parameters(self):
        properties = search_apps.TOOL["inputSchema"]["properties"]
        self.assertNotIn("favoritesOnly", properties)
        self.assertNotIn("favoriteFolder", properties)
        with patch.object(search_apps, "api_get", new_callable=AsyncMock, return_value=({"data": []}, None)) as api:
            await search_apps.handle({"search": "fitness", "favoritesOnly": True, "favoriteFolder": "Research"}, "key")
            api.assert_awaited_once_with("/api/v1/apps", {"search": "fitness"}, "key")

    async def test_unfiled_favorites_use_the_separate_endpoint(self):
        with patch.object(list_favorite_apps, "api_get", new_callable=AsyncMock, return_value=({"data": []}, None)) as api:
            await list_favorite_apps.handle({"folder": ""}, "key")
            api.assert_awaited_once_with("/api/v1/favorites/apps", {"folder": ""}, "key")
            self.assertEqual(_clean_params(api.call_args.args[1]), {"folder": ""})

    async def test_list_forwards_pagination_and_folder_only(self):
        with patch.object(list_favorite_apps, "api_get", new_callable=AsyncMock, return_value=({"data": []}, None)) as api:
            await list_favorite_apps.handle({"folder": "Research", "limit": 5, "cursor": 10, "userId": "other"}, "key")
            api.assert_awaited_once_with("/api/v1/favorites/apps", {"folder": "Research", "limit": 5, "cursor": 10}, "key")

    async def test_errors_are_returned_as_tool_errors(self):
        with patch.object(list_favorite_apps, "api_get", new_callable=AsyncMock, return_value=(None, "Unauthorized")):
            self.assertTrue((await list_favorite_apps.handle({}, "key"))["isError"])
