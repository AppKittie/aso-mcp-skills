"""ChatGPT's OAuth-protected endpoint, alongside the existing API-key MCP."""

from .api import api_get
from .constants import API_BASE
from .http import json_response
from .oauth import OAUTH_SCOPE, PUBLIC_TOOLS, request_origin


MCP_PATH = "/chatgpt/mcp"
RESOURCE = "https://mcp.appkittie.com" + MCP_PATH
METADATA_PATH = "/.well-known/oauth-protected-resource" + MCP_PATH


def resource_metadata():
    return {
        "resource": RESOURCE,
        "authorization_servers": [API_BASE],
        "scopes_supported": [OAUTH_SCOPE],
        "bearer_methods_supported": ["header"],
        "resource_documentation": API_BASE + "/docs",
        "resource_policy_uri": API_BASE + "/privacy",
        "resource_tos_uri": API_BASE + "/terms",
    }


def auth_challenge(request):
    return json_response(
        {"error": "invalid_token", "error_description": "Connect your AppKittie account"},
        status=401,
        extra_headers={
            "WWW-Authenticate": (
                'Bearer error="invalid_token", '
                f'resource_metadata="{request_origin(request)}{METADATA_PATH}", '
                f'scope="{OAUTH_SCOPE}"'
            ),
            "Cache-Control": "no-store",
        },
    )


async def validate_token(token):
    """Validate opaque OAuth tokens with the issuer; never accept API keys here."""
    if not token or not token.startswith("ak_oauth_access_") or len(token) > 128:
        return False
    data, error = await api_get("/api/mcp/oauth/session", {}, token)
    if error:
        if "HTTP 401" in error:
            return False
        raise RuntimeError("AppKittie authorization service unavailable")
    return (
        isinstance(data, dict)
        and data.get("active") is True
        and data.get("scope") == OAUTH_SCOPE
        and data.get("resource") == RESOURCE
        and data.get("issuer") == API_BASE
    )


def tool_definitions(tools):
    # Copy descriptors so metadata for existing MCP clients stays independent.
    result = []
    for tool in tools:
        scheme = (
            {"type": "noauth"} if tool["name"] in PUBLIC_TOOLS else
            {"type": "oauth2", "scopes": [OAUTH_SCOPE]}
        )
        result.append({
            **tool,
            "annotations": {**tool.get("annotations", {}), "destructiveHint": False},
            "securitySchemes": [scheme],
            "_meta": {**tool.get("_meta", {}), "securitySchemes": [scheme]},
        })
    return result
