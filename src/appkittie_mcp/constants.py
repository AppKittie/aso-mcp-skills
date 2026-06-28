API_BASE = "https://appkittie.com"
PROTOCOL_VERSION = "2025-03-26"
SERVER_NAME = "appkittie"
SERVER_VERSION = "1.0.0"

SORT_BY_OPTIONS = [
    "growth", "rating", "reviews", "updated", "released",
    "app_updated", "downloads", "revenue", "trending", "newest",
]

SORT_ORDERS = ["asc", "desc"]

GROWTH_PERIODS = ["7d", "14d", "30d", "60d", "90d"]
GROWTH_METRICS = ["reviews"]

CONTENT_RATINGS = ["all", "4+", "9+", "12+", "17+"]
PRICE_TYPES = ["all", "free", "paid"]
STORE_SOURCES = ["apple_mobile", "google_mobile"]

AD_SOURCE_OPTIONS = ["all", "meta", "google"]
AD_MEDIA_TYPES = ["all", "image", "video"]
AD_STATUSES = ["all", "active", "inactive"]
AD_SORT_BY_OPTIONS = [
    "start_date",
    "end_date",
    "app_downloads",
    "app_revenue",
    "app_released_timestamp",
    "app_updated_timestamp",
]
AD_TEXT_SEARCH_FIELDS = [
    "creative_text",
    "title",
    "body",
    "caption",
    "description",
    "label",
    "cta_text",
    "page_name",
    "developer",
    "app_title",
    "category",
]

HISTORICAL_PERIODS = ["30d", "90d", "300d", "all"]
HISTORICAL_METRICS = [
    "reviews",
    "current_version_reviews",
    "score",
    "current_version_score",
    "size",
    "price",
    "downloads",
    "revenue",
    "mau",
    "dau",
]

APP_STORE_COUNTRY_CODES = [
    "US", "GB", "CA", "AU", "NZ", "IE",
    "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH", "PT", "LU",
    "SE", "NO", "DK", "FI",
    "JP", "KR", "CN", "TW", "HK", "SG",
]

