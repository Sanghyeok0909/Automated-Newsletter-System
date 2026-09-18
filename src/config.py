"""
Zero-Capital Newsletter Configuration
Central authoritative settings for candidate retrieval, ranking, analysis, and generation.
"""

# Authoritative Selection Target
ARTICLES_PER_PUBLISHER = 5
CANDIDATES_PER_PUBLISHER = 20
FRESHNESS_HOURS = 24

# Canonical Publishers Registry
PUBLISHERS = [
    {
        "name": "The Verge",
        "slug": "verge",
        "mark": "V",
        "color": "#e0005a",
        "direct_rss": "https://www.theverge.com/rss/index.xml",
        "google_news_rss": "https://news.google.com/rss/search?q=site:theverge.com+when:1d&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "name": "TechCrunch",
        "slug": "techcrunch",
        "mark": "TC",
        "color": "#029924",
        "direct_rss": "https://techcrunch.com/feed/",
        "google_news_rss": "https://news.google.com/rss/search?q=site:techcrunch.com+when:1d&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "name": "Ars Technica",
        "slug": "arstechnica",
        "mark": "AT",
        "color": "#ff4e00",
        "direct_rss": "https://feeds.arstechnica.com/arstechnica/index",
        "google_news_rss": "https://news.google.com/rss/search?q=site:arstechnica.com+when:1d&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "name": "MIT Tech Review",
        "slug": "mit",
        "mark": "MIT",
        "color": "#333333",
        "direct_rss": "https://www.technologyreview.com/feed/",
        "google_news_rss": "https://news.google.com/rss/search?q=site:technologyreview.com+when:1d&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "name": "The Information",
        "slug": "theinformation",
        "mark": "TI",
        "color": "#0d253f",
        "direct_rss": "https://www.theinformation.com/feed",
        "google_news_rss": "https://news.google.com/rss/search?q=site:theinformation.com+when:1d&hl=en-US&gl=US&ceid=US:en"
    }
]

# Quick-lookup maps
PUBLISHER_BY_NAME = {p["name"]: p for p in PUBLISHERS}
PUBLISHER_BY_SLUG = {p["slug"]: p for p in PUBLISHERS}
TARGET_FEEDS = {p["name"]: p["direct_rss"] for p in PUBLISHERS}
GOOGLE_NEWS_FEEDS = {p["name"]: p["google_news_rss"] for p in PUBLISHERS}

# Deterministic Ranking Rubric Configuration
# Component 1: Material industry, market, or public impact (0–35)
IMPACT_SIGNALS = [
    # Regulatory, antitrust, government & national security
    "antitrust", "lawsuit", "sues", "ftc", "doj", "european union", "eu", "dma", "gdpr",
    "regulation", "subpoena", "national security", "sanction", "export control",
    # M&A, IPO, Restructuring, Capital expenditure
    "acquisition", "acquires", "merger", "buyout", "ipo", "layoff", "restructuring",
    "billion", "$b", "valuation", "earnings", "revenue drop", "market cap",
    # Infrastructure, Outages & Zero-Days
    "zero-day", "vulnerability", "breach", "cyberattack", "exploit", "outage",
    "semiconductor", "tsmc", "asml", "foundry", "lithography", "gpu cluster",
    # Foundational Tech Shifts
    "openai", "anthropic", "google deepmind", "meta ai", "apple intelligence", "nvidia"
]

# Component 2: Relevance to technology and business decisions (0–25)
BUSINESS_SIGNALS = [
    "enterprise", "b2b", "commercialization", "monetization", "subscription", "pricing",
    "developer", "tooling", "api", "cloud", "aws", "azure", "infrastructure",
    "venture capital", "funding", "seed", "series a", "series b", "series c",
    "robotics", "humanoid", "autonomous", "energy grid", "nuclear", "data center"
]

# Component 3: New, substantive developments supported by evidence (0–20)
DEVELOPMENT_SIGNALS = [
    "launches", "unveils", "announces", "releases", "introduces", "rolls out",
    "open-source", "weights", "benchmark", "breakthrough", "architecture", "paper",
    "patent", "scientific discovery", "clinical"
]

# Component 5: Original reporting or distinctive evidence (0–10)
ORIGINAL_SIGNALS = [
    "exclusive", "scoop", "investigation", "sources say", "internal memo",
    "internal documents", "deep dive", "report:", "analysis:", "teardown"
]

# Exclusions / Penalties (Promotional, shopping, coupons, trivial login stubs)
PROMOTIONAL_SIGNALS = [
    "deal", "deals", "coupon", "promo code", "discount", "save $", "% off",
    "gift guide", "buying guide", "roundup: best", "cheap", "sponsored",
    "partner content", "affiliate", "review:", "best tv", "best laptop", "best phone"
]

LOW_SIGNAL_TITLES = [
    "login", "sign in", "subscribe", "newsletter", "podcast", "daily briefing",
    "roundup", "edition", "episode", "feed"
]
