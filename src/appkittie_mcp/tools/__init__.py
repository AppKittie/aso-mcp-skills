from . import batch_keyword_difficulty
from . import get_ad_detail
from . import get_app_detail
from . import get_app_historicals
from . import get_app_reviews
from . import get_keyword_difficulty
from . import get_supported_countries
from . import get_store_ranking_history
from . import list_creators
from . import list_organic_content
from . import list_store_rankings
from . import search_ads
from . import search_apps
from . import search_onboarding_screens


TOOL_MODULES = [
    search_apps,
    get_app_detail,
    get_app_historicals,
    list_store_rankings,
    get_store_ranking_history,
    search_ads,
    get_ad_detail,
    list_creators,
    list_organic_content,
    get_keyword_difficulty,
    batch_keyword_difficulty,
    get_supported_countries,
    get_app_reviews,
    search_onboarding_screens,
]

TOOLS = [module.TOOL for module in TOOL_MODULES]
TOOL_HANDLERS = {module.TOOL["name"]: module.handle for module in TOOL_MODULES}
