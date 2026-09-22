"""
Zero-Capital Newsletter Configuration
Central authoritative settings for candidate retrieval, ranking, analysis, and generation.
"""

import os
import re

# Authoritative Selection Target
ARTICLES_PER_PUBLISHER = 5
CANDIDATES_PER_PUBLISHER = 20
FRESHNESS_HOURS = 24
BATCH_SIZE = 5

# LLM Configuration & Bounds
# Verified standard models in Google Gemini API
PRIMARY_MODEL = "gemini-1.5-flash"
FALLBACK_MODEL = "gemini-3.8-flash"
VERIFIED_MODELS = [PRIMARY_MODEL, FALLBACK_MODEL]

API_TIMEOUT_SECONDS = 45.0
MAX_BATCH_RETRIES = 1
RATE_LIMIT_DELAY_SECONDS = 6.0

# Canonical Publishers Registry
PUBLISHERS = [
    {
        "name": "The Verge",
        "slug": "verge",
        "mark": "V",
        "color": "#e0005a",
        "direct_rss": "https://www.theverge.com/rss/index.xml",
        "alt_rss": "https://www.theverge.com/rss/front-page/index.xml",
        "google_news_rss": "https://news.google.com/rss/search?q=site:theverge.com+when:2d&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "name": "TechCrunch",
        "slug": "techcrunch",
        "mark": "TC",
        "color": "#029924",
        "direct_rss": "https://techcrunch.com/feed/",
        "alt_rss": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "google_news_rss": "https://news.google.com/rss/search?q=site:techcrunch.com+when:2d&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "name": "Ars Technica",
        "slug": "arstechnica",
        "mark": "AT",
        "color": "#ff4e00",
        "direct_rss": "https://feeds.arstechnica.com/arstechnica/index",
        "alt_rss": "https://arstechnica.com/feed/",
        "google_news_rss": "https://news.google.com/rss/search?q=site:arstechnica.com+when:2d&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "name": "MIT Tech Review",
        "slug": "mit",
        "mark": "MIT",
        "color": "#333333",
        "direct_rss": "https://www.technologyreview.com/feed/",
        "alt_rss": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        "google_news_rss": "https://news.google.com/rss/search?q=site:technologyreview.com+when:2d&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "name": "The Information",
        "slug": "theinformation",
        "mark": "TI",
        "color": "#0d253f",
        "direct_rss": "https://www.theinformation.com/feed",
        "alt_rss": "https://www.theinformation.com/feed",
        "google_news_rss": "https://news.google.com/rss/search?q=site:theinformation.com+when:2d&hl=en-US&gl=US&ceid=US:en"
    }
]

# Quick-lookup maps
PUBLISHER_BY_NAME = {p["name"]: p for p in PUBLISHERS}
PUBLISHER_BY_SLUG = {p["slug"]: p for p in PUBLISHERS}
TARGET_FEEDS = {p["name"]: p["direct_rss"] for p in PUBLISHERS}
GOOGLE_NEWS_FEEDS = {p["name"]: p["google_news_rss"] for p in PUBLISHERS}

# Deterministic Ranking Rubric Configuration
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

BUSINESS_SIGNALS = [
    "enterprise", "b2b", "commercialization", "monetization", "subscription", "pricing",
    "developer", "tooling", "api", "cloud", "aws", "azure", "infrastructure",
    "venture capital", "funding", "seed", "series a", "series b", "series c",
    "robotics", "humanoid", "autonomous", "energy grid", "nuclear", "data center"
]

DEVELOPMENT_SIGNALS = [
    "launches", "unveils", "announces", "releases", "introduces", "rolls out",
    "open-source", "weights", "benchmark", "breakthrough", "architecture", "paper",
    "patent", "scientific discovery", "clinical"
]

ORIGINAL_SIGNALS = [
    "exclusive", "scoop", "investigation", "sources say", "internal memo",
    "internal documents", "deep dive", "report:", "analysis:", "teardown"
]

# Financial / Market reporting whitelist tokens (these prevent accidental promotional tagging)
FINANCIAL_MARKET_TOKENS = [
    "bond", "bonds", "convertible", "offering", "ipo", "shares", "stock", "stocks",
    "notes", "debt", "valuation", "fund", "funding", "earnings", "quarterly", "revenue",
    "acquisition", "billion", "$b", "million", "$m", "market cap", "treasury", "yield"
]

# True Shopping / Commercial promotional patterns
SHOPPING_DEAL_REGEX = re.compile(
    r'\b(save \$\d+|\d+%\s*off|promo codes?|discount codes?|coupons?|gift guides?|buying guides?|buyer\'s guides?|roundup:?\s*best|lowest prices?|best prices? on|affiliate commission|best prime day)\b',
    re.IGNORECASE
)

PROMOTIONAL_SUBSTRINGS = [
    "sponsored by", "partner content", "review: our top", "cheap tech deals"
]

LOW_SIGNAL_TITLES = [
    "login", "sign in", "subscribe", "newsletter", "podcast", "daily briefing",
    "roundup", "edition", "episode", "feed"
]
