import json

from ..api import api_get
from ..rpc import tool_result


TOOL = {
    "name": "search_onboarding_screens",
    "description": "Browse mobile apps with onboarding screens by screen type, app search, category, or app slug. Each app is returned once with ordered onboarding_images and onboarding_image_designs: URL-paired design objects containing colors (name, hex, roles), typography (font family, confidence, size, line height, weight, spacing, color), ui_elements (name, kind, layout, appearance, corner radius), layout and notes. Designs cover only returned images and can be missing. Measurements are source screenshot pixels; font families are estimates. No video. Costs 1 credit per app.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "label": {
                "type": "string",
                "enum": [
                    "onboarding", "quiz", "paywall", "home", "permissions",
                    "feature_intro", "profile_setup", "welcome", "content",
                    "preferences", "other", "sign_up", "settings", "login",
                    "success", "subscription", "discount", "lesson", "search",
                    "checkout",
                ],
                "description": "Screen type to browse",
            },
            "appSlug": {"type": "string", "description": "Limit results to one app slug"},
            "search": {"type": "string", "description": "Full-text app search"},
            "categories": {"type": "array", "items": {"type": "string"}},
            "source": {"type": "string", "enum": ["apple_mobile", "google_mobile"]},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50},
            "cursor": {"type": "integer"},
        },
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    data, err = await api_get("/api/v1/onboarding/screens", args, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))
