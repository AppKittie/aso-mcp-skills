API_BASE = "https://www.appkittie.com"
PROTOCOL_VERSION = "2025-03-26"
SERVER_NAME = "appkittie"
SERVER_VERSION = "1.0.0"

SORT_BY_OPTIONS = [
    "growth", "rating", "reviews", "updated", "released",
    "app_updated", "downloads", "revenue", "downloads_growth",
    "revenue_growth", "trending", "newest",
]

SORT_ORDERS = ["asc", "desc"]

GROWTH_PERIODS = ["7d", "14d", "30d", "60d", "90d"]
GROWTH_METRICS = ["reviews"]

CONTENT_RATINGS = ["all", "4+", "9+", "12+", "17+"]
PRICE_TYPES = ["all", "free", "paid"]
STORE_SOURCES = ["apple_mobile", "google_mobile"]

AD_SOURCE_OPTIONS = ["all", "meta", "google", "tiktok"]
AD_MEDIA_TYPES = ["all", "image", "video"]
AD_STATUSES = ["all", "active", "inactive"]
AD_SORT_BY_OPTIONS = [
    "start_date",
    "end_date",
    "app_downloads",
    "app_revenue",
    "app_meta_ads_estimated_spend_7d_usd",
    "app_meta_ads_estimated_spend_30d_usd",
    "app_meta_ads_estimated_spend_90d_usd",
    "app_meta_ads_estimated_reach_7d",
    "app_meta_ads_estimated_reach_30d",
    "app_meta_ads_estimated_reach_90d",
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

# Every SDK name the build scanners store in an app's sdk.sdks, both stores
# (processors' sdk_signatures.json). Google Play names three of them
# differently: AppLovin, Cloud Firestore, Unity.
SDK_NAMES = [
    "Ably",
    "ACRA",
    "Adapty",
    "Adjust",
    "AFNetworking",
    "Alamofire",
    "Amplitude",
    "AppAuth",
    "AppLovin",
    "AppLovin MAX",
    "AppsFlyer",
    "Branch",
    "Braze",
    "Capacitor",
    "Chartboost",
    "CleverTap",
    "Cloud Firestore",
    "CocoaLumberjack",
    "Confiant",
    "ContextSDK",
    "Cordova",
    "Datadog",
    "DGCharts",
    "Expo",
    "Facebook Aggregated Event Measurement",
    "Facebook Core SDK",
    "Facebook Login",
    "Facebook Share",
    "Firebase Analytics",
    "Firebase Authentication",
    "Firebase Cloud Messaging",
    "Firebase Core",
    "Firebase Crashlytics",
    "Firebase Firestore",
    "Firebase Installations",
    "Firebase Performance",
    "Firebase Remote Config",
    "Flutter",
    "FullStory",
    "Google Ads On-Device Conversion",
    "Google App Measurement",
    "Google Interactive Media Ads",
    "Google Mobile Ads / AdMob",
    "Google Play Billing",
    "Google Promises",
    "Google Sign-In",
    "Google User Messaging Platform",
    "Google Utilities",
    "GRDB",
    "GTM AppAuth",
    "GTM Session Fetcher",
    "Hermes",
    "IAB Open Measurement",
    "InMobi",
    "Intercom",
    "ironSource / Unity LevelPlay",
    "ironSource Ad Quality",
    "Kingfisher",
    "Lottie",
    "Meta Audience Network",
    "Mixpanel",
    "Moloco",
    "nanopb",
    "OneSignal",
    "OpenSSL",
    "Pangle",
    "PhoneNumberKit",
    "PostHog",
    "Prebid Mobile",
    "React Native",
    "Realm",
    "RevenueCat",
    "RevenueCat Paywalls",
    "Rive",
    "SDWebImage",
    "Segment",
    "Sentry",
    "SnapKit",
    "Stripe",
    "Superwall",
    "Unified ID 2.0",
    "Unity",
    "Unity Ads",
    "Unity Engine",
    "Vungle / Liftoff Monetize",
    "Zendesk",
    "ZIPFoundation",
]
