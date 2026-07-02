import json
import re
from urllib.parse import parse_qs, quote, urlparse

from js import Headers, fetch
import js
from pyodide.ffi import to_js

from .api import api_get


def as_str(value):
    if value is None:
        return ""
    return str(value).strip()


def _sanitize_slug_part(part):
    part = part.lower().replace("_", "-").replace(" ", "-")
    part = re.sub(r"[^a-z0-9-]", "", part)
    part = re.sub(r"-+", "-", part)
    return part.strip("-")


def create_app_slug_from_store_url(raw):
    value = as_str(raw)
    if not value:
        return None

    try:
        parsed = urlparse(value)
    except Exception:
        return None

    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    if host == "play.google.com" and "/store/apps/details" in parsed.path:
        package = as_str(parse_qs(parsed.query).get("id", [""])[0])
        package_slug = _sanitize_slug_part(package)
        return f"google-play-{package_slug}"[:128] if package_slug else None

    if host not in ["apps.apple.com", "itunes.apple.com"]:
        return None

    parts = [part for part in parsed.path.split("/") if part]
    try:
        app_idx = parts.index("app")
    except ValueError:
        return None

    if app_idx + 1 >= len(parts):
        return None

    app_name = _sanitize_slug_part(parts[app_idx + 1])
    app_id = _sanitize_slug_part(parts[app_idx + 2] if app_idx + 2 < len(parts) else "")
    if not app_name:
        return None

    slug = f"app-{app_name}-{app_id}" if app_id else f"app-{app_name}"
    return slug[:128]


def google_play_slug_from_package(raw):
    value = as_str(raw)
    if not re.match(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$", value):
        return None
    package_slug = _sanitize_slug_part(value)
    return f"google-play-{package_slug}"[:128] if package_slug else None


def looks_like_app_slug(raw):
    value = as_str(raw)
    return value.startswith("app-") or value.startswith("google-play-")


def is_apple_store_id(raw):
    return bool(re.match(r"^\d+$", as_str(raw)))


async def lookup_apple_app_slug(raw):
    store_id = as_str(raw)
    if not is_apple_store_id(store_id):
        return None

    headers = Headers.new()
    headers.set("Accept", "application/json")

    resp = await fetch(
        f"https://itunes.apple.com/lookup?id={quote(store_id, safe='')}",
        to_js({"method": "GET", "headers": headers}, dict_converter=js.Object.fromEntries),
    )
    if resp.status != 200:
        return None

    try:
        data = json.loads(await resp.text())
    except json.JSONDecodeError:
        return None

    results = data.get("results", []) if isinstance(data, dict) else []
    if not results:
        return None

    app = results[0]
    if not isinstance(app, dict):
        return None

    track_url = as_str(app.get("trackViewUrl"))
    slug = create_app_slug_from_store_url(track_url)
    if slug:
        return slug

    name = _sanitize_slug_part(
        as_str(app.get("trackName")) or as_str(app.get("trackCensoredName"))
    )
    return f"app-{name}-id{store_id}"[:128] if name else None


def first_app_identifier(args):
    for key in ["appStoreUrl", "appUrl", "url", "appStoreId", "storeId", "appId"]:
        raw_identifier = as_str(args.get(key))
        if raw_identifier:
            return key, raw_identifier
    return None, ""


async def resolve_app_path_identifier(args, _api_key):
    explicit_slug = as_str(args.get("appSlug")) or as_str(args.get("app_slug"))
    if explicit_slug:
        return explicit_slug, None

    key, raw_identifier = first_app_identifier(args)
    if not raw_identifier:
        return None, "Error: one of 'appSlug', 'appId', 'appStoreId', or 'appStoreUrl' is required."

    derived_slug = (
        create_app_slug_from_store_url(raw_identifier)
        or google_play_slug_from_package(raw_identifier)
    )
    if derived_slug:
        return derived_slug, None

    if looks_like_app_slug(raw_identifier):
        return raw_identifier, None

    if key in ["appStoreId", "storeId"]:
        apple_slug = await lookup_apple_app_slug(raw_identifier)
        if apple_slug:
            return apple_slug, None

    return raw_identifier, None


async def api_get_app_resource(app_identifier, suffix, params, api_key):
    data, err = await api_get(
        f"/api/v1/apps/{quote(app_identifier, safe='')}{suffix}",
        params,
        api_key,
    )
    if not err or not is_apple_store_id(app_identifier):
        return data, err

    apple_slug = await lookup_apple_app_slug(app_identifier)
    if not apple_slug or apple_slug == app_identifier:
        return data, err

    return await api_get(
        f"/api/v1/apps/{quote(apple_slug, safe='')}{suffix}",
        params,
        api_key,
    )

