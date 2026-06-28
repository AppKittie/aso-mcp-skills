"""
AppKittie MCP Server - Cloudflare Workers (Python)

This file is intentionally small: it owns the Cloudflare Worker entrypoint and
MCP JSON-RPC routing. Tool definitions and handlers live in appkittie_mcp/tools.
"""

import json

from js import Headers, Response

from appkittie_mcp.constants import PROTOCOL_VERSION, SERVER_NAME, SERVER_VERSION
from appkittie_mcp.instructions import INSTRUCTIONS
from appkittie_mcp.prompts import PROMPTS, render_prompt
from appkittie_mcp.rpc import rpc_error, rpc_success, tool_result
from appkittie_mcp.tools import TOOLS, TOOL_HANDLERS


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, Mcp-Session-Id",
    "Access-Control-Max-Age": "86400",
}


def json_response(body, status=200):
    headers = Headers.new()
    headers.set("Content-Type", "application/json")
    for key, value in CORS_HEADERS.items():
        headers.set(key, value)
    return Response.new(json.dumps(body), status=status, headers=headers)


def empty_response(status=202):
    headers = Headers.new()
    for key, value in CORS_HEADERS.items():
        headers.set(key, value)
    return Response.new("", status=status, headers=headers)


def extract_api_key(request):
    auth = request.headers.get("Authorization") or ""
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


def handle_initialize(req_id):
    return rpc_success(req_id, {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {"tools": {}, "prompts": {}},
        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        "instructions": INSTRUCTIONS,
    })


def handle_tools_list(req_id):
    return rpc_success(req_id, {"tools": TOOLS})


def handle_prompts_list(req_id):
    return rpc_success(req_id, {"prompts": PROMPTS})


def handle_prompts_get(req_id, params):
    name = params.get("name", "")
    arguments = params.get("arguments", [])
    prompt = next((item for item in PROMPTS if item["name"] == name), None)
    if not prompt:
        return rpc_error(req_id, -32602, f"Unknown prompt: {name}")
    return rpc_success(req_id, {"messages": render_prompt(name, arguments)})


async def handle_tool_call(req_id, params, api_key):
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})
    handler = TOOL_HANDLERS.get(tool_name)

    if not handler:
        return rpc_error(req_id, -32602, f"Unknown tool: {tool_name}")

    if not api_key:
        if tool_name == "get_supported_countries":
            return await _call_tool(req_id, handler, arguments, "")

        return rpc_success(
            req_id,
            tool_result(
                "Authentication required. Pass your AppKittie API key as a "
                "Bearer token in the Authorization header.",
                is_error=True,
            ),
        )

    return await _call_tool(req_id, handler, arguments, api_key)


async def _call_tool(req_id, handler, arguments, api_key):
    try:
        result = await handler(arguments, api_key)
        return rpc_success(req_id, result)
    except Exception as exc:
        return rpc_success(
            req_id,
            tool_result(f"Tool execution error: {str(exc)}", is_error=True),
        )


async def handle_rpc(rpc, api_key, env):
    """Process a single JSON-RPC message."""
    method = rpc.get("method", "")
    req_id = rpc.get("id")
    params = rpc.get("params", {})
    is_notification = req_id is None

    if method == "initialize":
        return handle_initialize(req_id)

    if method == "notifications/initialized":
        return None

    if method == "ping":
        return rpc_success(req_id, {})

    if method == "tools/list":
        return handle_tools_list(req_id)

    if method == "prompts/list":
        return handle_prompts_list(req_id)

    if method == "prompts/get":
        return handle_prompts_get(req_id, params)

    if method == "tools/call":
        return await handle_tool_call(req_id, params, api_key)

    if is_notification:
        return None

    return rpc_error(req_id, -32601, f"Method not found: {method}")


async def on_fetch(request, env):
    if request.method == "OPTIONS":
        return empty_response(204)

    if request.method == "GET":
        return json_response({
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "protocol": "MCP",
            "description": (
                "AppKittie MCP Server - discover App Store and Google Play apps, "
                "research ASO keywords, and access download/revenue intelligence."
            ),
            "tools": len(TOOLS),
            "docs": "https://appkittie.com/docs",
        })

    if request.method == "DELETE":
        return empty_response(200)

    if request.method != "POST":
        return json_response(
            {"error": "Method not allowed. Use POST for MCP messages."},
            status=405,
        )

    try:
        body_text = await request.text()
        rpc = json.loads(body_text)
    except Exception:
        return json_response(rpc_error(None, -32700, "Parse error: invalid JSON"))

    api_key = extract_api_key(request)

    if isinstance(rpc, list):
        results = []
        for message in rpc:
            result = await handle_rpc(message, api_key, env)
            if result is not None:
                results.append(result)
        if results:
            return json_response(results)
        return empty_response()

    result = await handle_rpc(rpc, api_key, env)
    if result is None:
        return empty_response()
    return json_response(result)

