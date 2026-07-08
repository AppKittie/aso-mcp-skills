import json

from js import Headers, Response


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": (
        "Content-Type, Authorization, Mcp-Session-Id, MCP-Protocol-Version, Accept"
    ),
    "Access-Control-Expose-Headers": "WWW-Authenticate, Mcp-Session-Id",
    "Access-Control-Max-Age": "86400",
}


def apply_cors(headers):
    for key, value in CORS_HEADERS.items():
        headers.set(key, value)
    return headers


def json_response(body, status=200, extra_headers=None):
    headers = Headers.new()
    headers.set("Content-Type", "application/json")
    apply_cors(headers)
    if extra_headers:
        for key, value in extra_headers.items():
            headers.set(key, value)
    return Response.new(json.dumps(body), status=status, headers=headers)


def html_response(body, status=200):
    headers = Headers.new()
    headers.set("Content-Type", "text/html; charset=utf-8")
    apply_cors(headers)
    return Response.new(body, status=status, headers=headers)


def empty_response(status=202):
    headers = Headers.new()
    apply_cors(headers)
    return Response.new("", status=status, headers=headers)


def redirect_response(url, status=302):
    headers = Headers.new()
    headers.set("Location", url)
    apply_cors(headers)
    return Response.new("", status=status, headers=headers)
