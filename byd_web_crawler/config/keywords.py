BYD_KEYWORDS_EN = [
    "BYD", "BYD car", "BYD EV", "BYD electric",
    "BYD Atto 3", "BYD Seal", "BYD Dolphin", "BYD Han",
    "BYD Tang", "BYD Sealion 6", "BYD Sealion 7",
    "BYD Thailand",
]

BYD_KEYWORDS_TH = [
    "BYD", "บีวายดี", "รถ BYD", "รถไฟฟ้า BYD",
    "BYD Atto", "BYD Seal", "BYD Dolphin",
    "BYD Han", "BYD Tang", "BYD Sealion",
]

# --- Per-platform search terms ---

PANTIP_SEARCH_TERMS = ["BYD", "บีวายดี", "รถ BYD"]
# Pantip automotive board tag
PANTIP_BOARD_TAG = "รถยนต์"

YOUTUBE_SEARCH_TERMS = [
    "BYD Thailand review",
    "รีวิว BYD",
    "BYD Atto 3 review",
    "BYD Seal review",
    "BYD Dolphin review",
    "BYD electric Thailand",
    "ซื้อ BYD",
]

# Twitter API v2 query strings (lang filter + retweet exclusion)
TWITTER_QUERIES = [
    "BYD -is:retweet lang:th",
    "บีวายดี -is:retweet",
    "BYD Thailand -is:retweet lang:en",
    "#BYD -is:retweet",
]

# Facebook public pages to scrape (page slug or vanity URL name)
FACEBOOK_PAGES = [
    "BYD.Thailand",
]

# Facebook public groups to scrape (numeric ID or group slug)
FACEBOOK_GROUPS = [
    "2389905174463399",  # Thai EV group (numeric ID)
    "bydthailand",       # BYD Thailand owners group
]

# Aspect labels used in LLM deep analysis
SENTIMENT_ASPECTS = [
    "price",
    "range",
    "charging",
    "safety",
    "design",
    "after_sales_service",
    "reliability",
    "brand_trust",
]
