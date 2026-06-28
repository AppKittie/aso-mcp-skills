from . import batch_keyword_difficulty
from . import get_ad_detail
from . import get_app_detail
from . import get_app_historicals
from . import get_app_reviews
from . import get_keyword_difficulty
from . import get_supported_countries
from . import list_creators
from . import list_organic_content
from . import search_ads
from . import search_apps


TOOL_MODULES = [
    search_apps,
    get_app_detail,
    get_app_historicals,
    search_ads,
    get_ad_detail,
    list_creators,
    list_organic_content,
    get_keyword_difficulty,
    batch_keyword_difficulty,
    get_supported_countries,
    get_app_reviews,
]

TOOLS = [module.TOOL for module in TOOL_MODULES]
TOOL_HANDLERS = {module.TOOL["name"]: module.handle for module in TOOL_MODULES}

