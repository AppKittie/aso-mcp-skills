#!/usr/bin/env python3
"""Validate and package only the explicitly listed ChatGPT plugin files."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "chatgpt-plugin" / "appkittie"
FILES = (
    "plugin.json", "mcp.json", ".codex-plugin/plugin.json", ".mcp.json",
    "skills/app-research/SKILL.md", "assets/icon.png",
)


def manifests():
    manifest = json.loads((PLUGIN / "plugin.json").read_text())
    mcp = json.loads((PLUGIN / "mcp.json").read_text())
    return manifest, mcp


def compatibility(manifest, mcp):
    legacy = {k: v for k, v in manifest.items() if k not in ("$schema", "extensions")}
    legacy.update({
        "skills": "./skills/", "mcpServers": "./.mcp.json",
        "interface": manifest["extensions"]["com.openai"]["interface"],
    })
    # The portable manifest supplies submission metadata. This fallback keeps
    # compatibility with the plugin-creator validator and older desktop hosts.
    servers = {name: {"url": server["url"]} for name, server in mcp["mcpServers"].items()}
    return legacy, {"mcpServers": servers}


def validate(manifest, mcp):
    if manifest["name"] != PLUGIN.name or not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
        raise ValueError("Invalid plugin identity/version")
    servers = mcp["mcpServers"]
    if set(servers) != {"appkittie"}:
        raise ValueError("Expected exactly the AppKittie MCP server")
    server = servers["appkittie"]
    if server["type"] != "streamable-http" or server["url"] != "https://mcp.appkittie.com/chatgpt/mcp":
        raise ValueError("Unexpected MCP endpoint")
    auth = server["extensions"]["com.openai"]["auth"]
    if auth["type"] != "mixed" or auth["client"] != {
        "mode": "provided", "clientId": "appkittie-chatgpt", "tokenEndpointAuthMethod": "none",
    } or auth["baseScopes"] != ["appkittie:read"]:
        raise ValueError("Unexpected OAuth configuration")
    for field, endpoint in (("authorizationUrl", "authorize"), ("tokenUrl", "token")):
        if auth[field] != "https://www.appkittie.com/api/mcp/oauth/" + endpoint:
            raise ValueError("Unexpected OAuth endpoint")
    metadata = manifest["extensions"]["com.openai"]
    cases = metadata["review"]["test_cases"]
    if len(cases["positive"]) < 5 or len(cases["negative"]) < 3:
        raise ValueError("Review scenarios are missing")
    for prompt in metadata["interface"]["defaultPrompt"]:
        if not isinstance(prompt, str) or len(prompt) > 128:
            raise ValueError("Invalid starter prompt")
    for field in ("composerIcon", "logo"):
        if metadata["interface"][field] != "./assets/icon.png":
            raise ValueError("Unpackaged icon reference")
    if not (PLUGIN / "assets/icon.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG icon")
    skill = (PLUGIN / "skills/app-research/SKILL.md").read_text()
    if not skill.startswith("---\nname: app-research\ndescription:"):
        raise ValueError("Invalid skill frontmatter")
    for name in FILES:
        path = PLUGIN / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(PLUGIN.resolve()):
            raise ValueError(f"Unsafe or missing package file: {name}")
        if path.suffix == ".json":
            payload = json.loads(path.read_text())
            def check(value):
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key in {"clientSecret", "headers", "env", "apps", "hooks"}:
                            raise ValueError(f"Credentials or unsupported submission field: {key}")
                        check(child)
                elif isinstance(value, list):
                    for child in value:
                        check(child)
                elif isinstance(value, str) and any(marker in value for marker in ("[TODO:", "YOUR_API_KEY", "ak_oauth_")):
                    raise ValueError("Placeholder or credential in package")
            check(payload)


def build(output=None):
    manifest, mcp = manifests()
    legacy, legacy_mcp = compatibility(manifest, mcp)
    (PLUGIN / ".codex-plugin").mkdir(exist_ok=True)
    for name, value in ((".codex-plugin/plugin.json", legacy), (".mcp.json", legacy_mcp)):
        (PLUGIN / name).write_text(json.dumps(value, indent=2) + "\n")
    validate(manifest, mcp)
    output = output or REPO / "dist" / f"appkittie-chatgpt-{manifest['version']}.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(FILES):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (PLUGIN / name).read_bytes())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() or set(archive.namelist()) != set(FILES):
            raise ValueError("Archive integrity check failed")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".zip.sha256").write_text(f"{digest}  {output.name}\n")
    print(f"Built {output} ({output.stat().st_size} bytes; {len(FILES)} files)")
    print(f"SHA256 {digest}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    build(args.output)
