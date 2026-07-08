import base64
import hashlib
import html
import json
import time
from urllib.parse import parse_qs, urlencode, unquote, urlparse

from .http import html_response, json_response, redirect_response


DEFAULT_OAUTH_CLIENT_ID = "appkittie-claude"
OAUTH_SCOPE = "appkittie:read"
OAUTH_CODE_TTL_SECONDS = 600
PUBLIC_TOOLS = {"get_supported_countries"}


def env_get(env, name, default=None):
    if env is None:
        return default

    try:
        value = getattr(env, name)
        if value is not None:
            return str(value)
    except Exception:
        pass

    try:
        value = env.get(name)
        if value is not None:
            return str(value)
    except Exception:
        pass

    try:
        value = env[name]
        if value is not None:
            return str(value)
    except Exception:
        pass

    return default


def allowed_oauth_client_ids(env):
    raw = (
        env_get(env, "OAUTH_CLIENT_IDS")
        or env_get(env, "OAUTH_CLIENT_ID")
        or env_get(env, "APPKITTIE_OAUTH_CLIENT_IDS")
        or env_get(env, "APPKITTIE_OAUTH_CLIENT_ID")
        or DEFAULT_OAUTH_CLIENT_ID
    )
    return {item.strip() for item in raw.split(",") if item.strip()}


def is_oauth_client_allowed(client_id, env):
    return bool(client_id and client_id in allowed_oauth_client_ids(env))


def request_origin(request):
    parsed = urlparse(str(request.url))
    return f"{parsed.scheme}://{parsed.netloc}"


def request_path(request):
    return urlparse(str(request.url)).path or "/"


def metadata_url_for_resource(request):
    origin = request_origin(request)
    path = request_path(request)
    if path == "/":
        return f"{origin}/.well-known/oauth-protected-resource"
    return f"{origin}/.well-known/oauth-protected-resource{path}"


def metadata_resource_from_request(request):
    origin = request_origin(request)
    path = request_path(request)
    prefix = "/.well-known/oauth-protected-resource"
    suffix = path[len(prefix):] if path.startswith(prefix) else ""
    if suffix and suffix != "/":
        return f"{origin}{suffix}"
    return origin


def authorization_server_metadata(request):
    origin = request_origin(request)
    return {
        "issuer": origin,
        "authorization_endpoint": f"{origin}/authorize",
        "token_endpoint": f"{origin}/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "scopes_supported": [OAUTH_SCOPE],
        "token_endpoint_auth_methods_supported": [
            "client_secret_post",
            "client_secret_basic",
        ],
        "code_challenge_methods_supported": ["S256"],
    }


def protected_resource_metadata(request):
    return {
        "resource": metadata_resource_from_request(request),
        "authorization_servers": [request_origin(request)],
        "bearer_methods_supported": ["header"],
        "scopes_supported": [OAUTH_SCOPE],
    }


def auth_required_response(request):
    metadata_url = metadata_url_for_resource(request)
    authenticate = (
        'Bearer error="invalid_token", '
        'error_description="Authentication required", '
        f'resource_metadata="{metadata_url}", '
        f'scope="{OAUTH_SCOPE}"'
    )
    return json_response(
        {
            "error": "invalid_token",
            "error_description": "Authentication required",
        },
        status=401,
        extra_headers={"WWW-Authenticate": authenticate},
    )


def query_params(request):
    parsed = urlparse(str(request.url))
    return {
        key: values[-1] if values else ""
        for key, values in parse_qs(parsed.query, keep_blank_values=True).items()
    }


async def read_form(request):
    body_text = await request.text()
    content_type = request.headers.get("Content-Type") or ""
    if "application/json" in content_type:
        try:
            body = json.loads(body_text)
            return {key: str(value) for key, value in body.items()}
        except Exception:
            return {}

    return {
        key: values[-1] if values else ""
        for key, values in parse_qs(body_text, keep_blank_values=True).items()
    }


def oauth_error(error, description, status=400):
    return json_response(
        {"error": error, "error_description": description},
        status=status,
    )


def oauth_redirect_error(redirect_uri, error, description, state=""):
    params = {"error": error, "error_description": description}
    if state:
        params["state"] = state
    separator = "&" if "?" in redirect_uri else "?"
    return redirect_response(f"{redirect_uri}{separator}{urlencode(params)}")


def encode_oauth_code(params):
    payload = dict(params)
    payload["exp"] = int(time.time()) + OAUTH_CODE_TTL_SECONDS
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_oauth_code(code):
    padding = "=" * (-len(code) % 4)
    raw = base64.urlsafe_b64decode((code + padding).encode("ascii"))
    return json.loads(raw.decode("utf-8"))


def pkce_s256(verifier):
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def validate_oauth_code(code, client_id, redirect_uri, code_verifier):
    try:
        payload = decode_oauth_code(code)
    except Exception:
        return "invalid_grant", "Invalid authorization code"

    if int(payload.get("exp", 0)) < int(time.time()):
        return "invalid_grant", "Authorization code expired"

    if payload.get("client_id") != client_id:
        return "invalid_grant", "Authorization code client mismatch"

    if payload.get("redirect_uri") != redirect_uri:
        return "invalid_grant", "Authorization code redirect mismatch"

    challenge = payload.get("code_challenge", "")
    if challenge:
        if not code_verifier:
            return "invalid_request", "Missing PKCE code_verifier"
        if pkce_s256(code_verifier) != challenge:
            return "invalid_grant", "Invalid PKCE code_verifier"

    return None, None


def calls_protected_tool(rpc, tool_handlers):
    messages = rpc if isinstance(rpc, list) else [rpc]
    for message in messages:
        if not isinstance(message, dict):
            continue
        if message.get("method") != "tools/call":
            continue
        params = message.get("params", {})
        tool_name = params.get("name", "")
        if tool_name in tool_handlers and tool_name not in PUBLIC_TOOLS:
            return True
    return False


def extract_basic_client_auth(request):
    auth = request.headers.get("Authorization") or ""
    if not auth.startswith("Basic "):
        return None, None

    try:
        decoded = base64.b64decode(auth[6:].strip()).decode("utf-8")
        client_id, client_secret = decoded.split(":", 1)
        return unquote(client_id), unquote(client_secret)
    except Exception:
        return None, None


def authorize_consent_page(params):
    hidden_fields = []
    for key, value in params.items():
        hidden_fields.append(
            '<input type="hidden" '
            f'name="{html.escape(key)}" value="{html.escape(value)}">'
        )

    client_id = html.escape(params.get("client_id", ""))
    scope = html.escape(params.get("scope", OAUTH_SCOPE))

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Connect AppKittie</title>
  <style>
    body {{
      align-items: center;
      background: #f7f8fb;
      color: #171923;
      display: flex;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      justify-content: center;
      margin: 0;
      min-height: 100vh;
    }}
    main {{
      background: #fff;
      border: 1px solid #dfe3ec;
      border-radius: 8px;
      box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
      max-width: 420px;
      padding: 28px;
      width: calc(100% - 40px);
    }}
    h1 {{
      font-size: 24px;
      line-height: 1.2;
      margin: 0 0 12px;
    }}
    p {{
      color: #4a5568;
      font-size: 15px;
      line-height: 1.5;
      margin: 0 0 20px;
    }}
    dl {{
      background: #f7f8fb;
      border-radius: 6px;
      display: grid;
      gap: 6px 12px;
      grid-template-columns: max-content 1fr;
      margin: 0 0 24px;
      padding: 14px;
    }}
    dt {{
      color: #64748b;
      font-size: 13px;
    }}
    dd {{
      font-size: 13px;
      margin: 0;
      overflow-wrap: anywhere;
    }}
    button {{
      background: #171923;
      border: 0;
      border-radius: 6px;
      color: #fff;
      cursor: pointer;
      font-size: 15px;
      font-weight: 600;
      min-height: 44px;
      padding: 0 18px;
      width: 100%;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Connect AppKittie</h1>
    <p>Authorize Claude to use your AppKittie API key for mobile app intelligence tools.</p>
    <dl>
      <dt>Client</dt><dd>{client_id}</dd>
      <dt>Scope</dt><dd>{scope}</dd>
    </dl>
    <form method="post" action="/authorize">
      {''.join(hidden_fields)}
      <button type="submit">Connect</button>
    </form>
  </main>
</body>
</html>"""


async def handle_authorize(request, env):
    params = query_params(request) if request.method == "GET" else await read_form(request)
    response_type = params.get("response_type", "")
    client_id = params.get("client_id", "")
    redirect_uri = params.get("redirect_uri", "")
    state = params.get("state", "")
    code_challenge = params.get("code_challenge", "")
    code_challenge_method = params.get("code_challenge_method", "")

    if response_type != "code":
        return oauth_error("unsupported_response_type", "Only authorization code is supported")

    if not is_oauth_client_allowed(client_id, env):
        return oauth_error("invalid_client", "Unknown OAuth client_id", status=401)

    if not redirect_uri:
        return oauth_error("invalid_request", "Missing redirect_uri")

    if code_challenge_method and code_challenge_method != "S256":
        return oauth_redirect_error(
            redirect_uri,
            "invalid_request",
            "Only S256 PKCE is supported",
            state,
        )

    if request.method == "GET":
        return html_response(authorize_consent_page(params))

    code = encode_oauth_code({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge,
    })
    callback_params = {"code": code}
    if state:
        callback_params["state"] = state
    separator = "&" if "?" in redirect_uri else "?"
    return redirect_response(f"{redirect_uri}{separator}{urlencode(callback_params)}")


async def handle_token(request, env):
    form = await read_form(request)
    basic_client_id, basic_client_secret = extract_basic_client_auth(request)
    grant_type = form.get("grant_type", "")
    client_id = basic_client_id or form.get("client_id", "")
    client_secret = basic_client_secret or form.get("client_secret", "")

    if not is_oauth_client_allowed(client_id, env):
        return oauth_error("invalid_client", "Unknown OAuth client_id", status=401)

    if grant_type == "authorization_code":
        code = form.get("code", "")
        redirect_uri = form.get("redirect_uri", "")
        error, description = validate_oauth_code(
            code,
            client_id,
            redirect_uri,
            form.get("code_verifier", ""),
        )
        if error:
            return oauth_error(error, description)

        api_key = client_secret

    elif grant_type == "refresh_token":
        api_key = client_secret or form.get("refresh_token", "")

    else:
        return oauth_error("unsupported_grant_type", "Unsupported grant_type")

    if not api_key:
        return oauth_error(
            "invalid_client",
            "OAuth client_secret must contain the AppKittie API key",
            status=401,
        )

    return json_response({
        "access_token": api_key,
        "token_type": "Bearer",
        "expires_in": 31536000,
        "refresh_token": api_key,
        "scope": form.get("scope", OAUTH_SCOPE),
    })
