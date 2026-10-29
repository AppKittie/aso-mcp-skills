import copy
import json
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch


js = sys.modules.setdefault("js", types.ModuleType("js"))
js.Headers = getattr(js, "Headers", object)
js.Response = getattr(js, "Response", object)
js.fetch = getattr(js, "fetch", object)
sys.modules.setdefault("pyodide", types.ModuleType("pyodide"))
ffi = sys.modules.setdefault("pyodide.ffi", types.ModuleType("pyodide.ffi"))
ffi.to_js = lambda value, **_kwargs: value

from appkittie_mcp import chatgpt
from appkittie_mcp.constants import API_BASE
from appkittie_mcp.tools import TOOLS
import worker


def response(body, status=200, extra_headers=None):
    return {"body": body, "status": status, "headers": extra_headers or {}}


def request(body, token=None, path=chatgpt.MCP_PATH):
    return types.SimpleNamespace(
        url="https://mcp.appkittie.com" + path,
        method="POST",
        headers={"Authorization": f"Bearer {token}"} if token else {},
        text=AsyncMock(return_value=json.dumps(body)),
    )


class ChatGPTTests(unittest.IsolatedAsyncioTestCase):
    def test_oauth_metadata_and_public_tool_are_explicit(self):
        original = copy.deepcopy(TOOLS)
        for tool in chatgpt.tool_definitions(TOOLS):
            expected = [{"type": "noauth"}] if tool["name"] == "get_supported_countries" else [{"type": "oauth2", "scopes": ["appkittie:read"]}]
            self.assertEqual(tool["securitySchemes"], expected)
            self.assertEqual(tool["_meta"]["securitySchemes"], expected)
        self.assertEqual(TOOLS, original)
        self.assertEqual(chatgpt.resource_metadata()["resource"], chatgpt.RESOURCE)

    async def test_opaque_token_validation_checks_all_claims(self):
        valid = {"active": True, "scope": "appkittie:read", "resource": chatgpt.RESOURCE, "issuer": API_BASE}
        for changes in ({}, {"active": False}, {"scope": "write"}, {"resource": "https://other.test"}, {"issuer": "https://other.test"}):
            with patch.object(chatgpt, "api_get", new=AsyncMock(return_value=({**valid, **changes}, None))):
                self.assertEqual(await chatgpt.validate_token("ak_oauth_access_test"), not changes)
        with patch.object(chatgpt, "api_get", new_callable=AsyncMock) as api:
            for token in (None, "", "appkittie_existing_key", "ak_oauth_refresh_test"):
                self.assertFalse(await chatgpt.validate_token(token))
            api.assert_not_awaited()

    async def test_issuer_outage_is_distinct_from_invalid_credentials(self):
        with patch.object(chatgpt, "api_get", new=AsyncMock(return_value=(None, "AppKittie API error (HTTP 401): invalid"))):
            self.assertFalse(await chatgpt.validate_token("ak_oauth_access_test"))
        with patch.object(chatgpt, "api_get", new=AsyncMock(return_value=(None, "AppKittie API error (HTTP 503): unavailable"))):
            with self.assertRaises(RuntimeError):
                await chatgpt.validate_token("ak_oauth_access_test")

    async def test_protected_tool_never_dispatches_without_valid_oauth(self):
        body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "search_apps", "arguments": {}}}
        with patch.object(chatgpt, "validate_token", new=AsyncMock(return_value=False)), patch.object(chatgpt, "json_response", side_effect=response), patch.object(worker, "handle_rpc", new_callable=AsyncMock) as dispatch:
            result = await worker.on_fetch(request(body, "appkittie_old_key"), {})
            self.assertEqual(result["status"], 401)
            self.assertIn(chatgpt.METADATA_PATH, result["headers"]["WWW-Authenticate"])
            dispatch.assert_not_awaited()

    async def test_public_discovery_and_countries_need_no_account(self):
        for method, params in (("initialize", {}), ("tools/list", {}), ("tools/call", {"name": "get_supported_countries", "arguments": {}})):
            with patch.object(chatgpt, "validate_token", new_callable=AsyncMock) as validate, patch.object(worker, "json_response", side_effect=response):
                result = await worker.on_fetch(request({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}), {})
                self.assertEqual(result["status"], 200)
                validate.assert_not_awaited()
                if method == "tools/list":
                    self.assertIn("securitySchemes", result["body"]["result"]["tools"][0])

    async def test_batch_auth_prevents_partial_execution(self):
        body = [{"id": 1, "method": "tools/call", "params": {"name": "get_supported_countries"}}, {"id": 2, "method": "tools/call", "params": {"name": "search_apps"}}]
        with patch.object(chatgpt, "validate_token", new=AsyncMock(return_value=False)), patch.object(chatgpt, "json_response", side_effect=response), patch.object(worker, "handle_rpc", new_callable=AsyncMock) as dispatch:
            self.assertEqual((await worker.on_fetch(request(body), {}))["status"], 401)
            dispatch.assert_not_awaited()

    async def test_valid_oauth_dispatch_and_legacy_key_are_supported(self):
        body = {"id": 1, "method": "tools/call", "params": {"name": "search_apps"}}
        for path, token in ((chatgpt.MCP_PATH, "ak_oauth_access_test"), ("/mcp", "appkittie_existing_key")):
            with patch.object(chatgpt, "validate_token", new=AsyncMock(return_value=True)) as validate, patch.object(worker, "handle_rpc", new=AsyncMock(return_value={"ok": True})) as dispatch, patch.object(worker, "json_response", side_effect=response):
                self.assertEqual((await worker.on_fetch(request(body, token, path), {}))["status"], 200)
                dispatch.assert_awaited_once_with(body, token, {}, path == chatgpt.MCP_PATH)
                self.assertEqual(validate.await_count, int(path == chatgpt.MCP_PATH))

    async def test_malformed_envelopes_are_rejected(self):
        for body in (None, [], "string", {"method": "tools/call", "params": []}, [False]):
            with patch.object(worker, "json_response", side_effect=response):
                result = await worker.on_fetch(request(body), {})
                self.assertEqual(result["body"]["error"]["code"], -32600)

    async def test_domain_verification_is_plain_text_and_requires_configuration(self):
        req = request({}, path="/.well-known/openai-apps-challenge")
        req.method = "GET"
        with patch("appkittie_mcp.http.text_response", side_effect=lambda body, status: (body, status)):
            self.assertEqual(await worker.on_fetch(req, {}), ("Not configured", 404))
            self.assertEqual(await worker.on_fetch(req, {"OPENAI_APPS_CHALLENGE": "challenge-value"}), ("challenge-value", 200))
