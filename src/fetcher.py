import urllib.parse
import feedparser
import json
import time
import os
import sys
import hashlib
import random
import calendar
import requests
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup

# Ensure local imports work whether executed from root or src/
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import (
    ARTICLES_PER_PUBLISHER,
    CANDIDATES_PER_PUBLISHER,
    FRESHNESS_HOURS,
    PUBLISHERS,
    TARGET_FEEDS,
    GOOGLE_NEWS_FEEDS,
    IMPACT_SIGNALS,
    BUSINESS_SIGNALS,
    DEVELOPMENT_SIGNALS,
    ORIGINAL_SIGNALS,
    FINANCIAL_MARKET_TOKENS,
    SHOPPING_DEAL_REGEX,
    PROMOTIONAL_SUBSTRINGS,
    LOW_SIGNAL_TITLES
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
]

def get_browser_headers(ua=None):
    if not ua:
        ua = random.choice(USER_AGENTS)
    return {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
        'Sec-Ch-Ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }

def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def canonicalize_url(url):
    """
    Strips marketing tracking parameters while preserving meaningful query parameters.
    """
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        tracking_keys = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'oc', 'ref', 'fbclid', 'gclid', 'mc_cid', 'mc_eid', 'source'
        }
        filtered_params = {k: v for k, v in query_params.items() if k.lower() not in tracking_keys}
        new_query = urllib.parse.urlencode(filtered_params, doseq=True)
        return urllib.parse.urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, ''
        ))
    except Exception:
        return url

def is_eligible_candidate(title, summary):
    """
    Filters out promotional shopping deals and trivial/login stubs,
    while explicitly preserving genuine financial, market, and business reporting
    (e.g., 'CoreWeave Prices $3.7B Convertible Bond Offering').
    """
    clean_t = title.strip().lower()
    if len(clean_t) < 10:
        return False
    if clean_t in LOW_SIGNAL_TITLES:
        return False
    for stub in LOW_SIGNAL_TITLES:
        if clean_t == stub or clean_t.startswith(f"{stub}:") or clean_t.endswith(f"- {stub}"):
            return False

    combined = f"{clean_t} {summary.lower()}"

    # Genuine financial / market reporting protection
    is_financial = any(tok in combined for tok in FINANCIAL_MARKET_TOKENS)
    if is_financial:
        if "affiliate commission" in combined or "promo code" in combined:
            return False
        return True

    # Check for shopping deal regex match
    if SHOPPING_DEAL_REGEX.search(combined):
        return False

    # Check for promotional substrings
    for promo in PROMOTIONAL_SUBSTRINGS:
        if promo in combined:
            return False

    return True

def score_article(title, summary, pub_date, now=None):
    """
    Deterministic heuristic scoring rubric (0–100):
    1. Material industry, market, or public impact: 0–35
    2. Relevance to technology and business decisions: 0–25
    3. New, substantive developments supported by evidence: 0–20
    4. Recency within eligible window: 0–10
    5. Original reporting or distinctive evidence: 0–10
    """
    if now is None:
        now = datetime.now(timezone.utc)
    if pub_date.tzinfo is None:
        pub_date = pub_date.replace(tzinfo=timezone.utc)

    combined_text = f"{title.lower()} {summary.lower()}"

    # 1. Material Impact (0–35)
    impact_matches = sum(1 for kw in IMPACT_SIGNALS if kw in combined_text)
    score_impact = min(35, impact_matches * 12)

    # 2. Tech & Business Relevance (0–25)
    business_matches = sum(1 for kw in BUSINESS_SIGNALS if kw in combined_text)
    score_business = min(25, business_matches * 9)

    # 3. Substantive Developments (0–20)
    dev_matches = sum(1 for kw in DEVELOPMENT_SIGNALS if kw in combined_text)
    dev_score = min(15, dev_matches * 8)
    if len(summary.strip()) >= 80:
        dev_score += 5
    score_dev = min(20, dev_score)

    # 4. Recency (0–10)
    age_hours = max(0, (now - pub_date).total_seconds() / 3600.0)
    if age_hours <= 6:
        score_recency = 10
    elif age_hours <= 12:
        score_recency = 7
    elif age_hours <= 18:
        score_recency = 4
    elif age_hours <= 24:
        score_recency = 1
    else:
        score_recency = 0

    # 5. Original Reporting (0–10)
    orig_matches = sum(1 for kw in ORIGINAL_SIGNALS if kw in combined_text)
    score_original = min(10, orig_matches * 5)

    total_score = score_impact + score_business + score_dev + score_recency + score_original
    return {
        "total_score": total_score,
        "impact": score_impact,
        "business": score_business,
        "development": score_dev,
        "recency": score_recency,
        "original": score_original
    }

def fetch_xml_data(url, max_retries=2):
    session = requests.Session()
    for attempt in range(max_retries + 1):
        headers = get_browser_headers()
        try:
            resp = session.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                content = resp.content
                if b'<rss' in content.lower() or b'<feed' in content.lower() or b'<?xml' in content.lower():
                    return content
                else:
                    print(f" -> [Non-XML Response] HTTP 200 but content is not XML ({url[:50]}...)")
            elif resp.status_code in (403, 429):
                print(f" -> [WAF/RateLimit] HTTP {resp.status_code} on attempt {attempt+1}/{max_retries+1} ({url[:50]}...)")
            else:
                print(f" -> [HTTP Error] HTTP {resp.status_code} ({url[:50]}...)")
        except Exception as e:
            print(f" -> [Network Fetch Failed] Attempt {attempt+1}/{max_retries+1} ({url[:50]}...): {e}")
        
        if attempt < max_retries:
            delay = 2.0 + random.uniform(0.5, 1.5) * (attempt + 1)
            time.sleep(delay)
    return None

def fetch_latest_articles():
    # Force cache invalidation: Purge any existing local cache files before fresh run
    for stale_file in ["src/articles.json", "src/fetcher_stats.json"]:
        if os.path.exists(stale_file):
            try:
                os.remove(stale_file)
                print(f"[Cache Invalidation] Removed stale cache: {stale_file}")
            except Exception as e:
                print(f"[Cache Invalidation] Warning: Failed to remove {stale_file}: {e}")

    now_utc = datetime.now(timezone.utc)
    freshness_threshold = now_utc - timedelta(hours=FRESHNESS_HOURS)

    all_publisher_candidates = {}
    diagnostic_stats = {}

    for publisher in PUBLISHERS:
        media = publisher["name"]
        direct_url = publisher["direct_rss"]
        alt_url = publisher.get("alt_rss")
        google_news_url = publisher["google_news_rss"]

        print(f"\nFetching candidates for {media}...")

        # Tier 1: Direct RSS
        xml_data = fetch_xml_data(direct_url)

        # Tier 2: Alternate RSS if direct feed blocked or invalid
        if not xml_data or (b'<rss' not in xml_data.lower() and b'<feed' not in xml_data.lower()):
            if alt_url and alt_url != direct_url:
                print(f" -> Direct RSS blocked or non-XML. Trying alternate feed: {alt_url[:60]}...")
                xml_data = fetch_xml_data(alt_url)

        # Tier 3: Google News fallback if direct & alternate feeds blocked or invalid
        if not xml_data or (b'<rss' not in xml_data.lower() and b'<feed' not in xml_data.lower()):
            print(f" -> Direct & Alt RSS blocked or non-XML. Falling back to Google News feed...")
            xml_data = fetch_xml_data(google_news_url)

        if not xml_data:
            print(f" -> [Warning] All feeds (direct, alternate, and Google News) failed for {media}.")
            diagnostic_stats[media] = {
                "status": "retrieval_failure",
                "raw_count": 0,
                "eligible_count": 0,
                "selected_count": 0
            }
            continue

        feed = feedparser.parse(xml_data)
        seen_canonical_urls = set()
        seen_title_roots = set()
        candidates = []

        raw_entries = feed.entries
        print(f" -> Retrieved {len(raw_entries)} raw feed entries.")

        for entry in raw_entries:
            if not (hasattr(entry, 'published_parsed') and entry.published_parsed):
                continue

            pub_date = datetime.fromtimestamp(calendar.timegm(entry.published_parsed), tz=timezone.utc)
            if pub_date < freshness_threshold:
                continue

            raw_title = entry.title if hasattr(entry, 'title') else ""
            clean_title = raw_title.split(' - ')[0] if ' - ' in raw_title else raw_title
            clean_title = clean_title.strip()

            summary = clean_html(entry.summary if hasattr(entry, 'summary') else "")
            canonical_url = canonicalize_url(entry.link if hasattr(entry, 'link') else "")

            if not is_eligible_candidate(clean_title, summary):
                continue

            # Deduplication
            if canonical_url in seen_canonical_urls:
                continue
            seen_canonical_urls.add(canonical_url)

            title_root = "".join(c for c in clean_title.lower() if c.isalnum())[:35]
            if title_root in seen_title_roots:
                continue
            seen_title_roots.add(title_root)

            # Heuristic importance scoring
            score_data = score_article(clean_title, summary, pub_date, now_utc)
            title_hash = int(hashlib.md5(clean_title.encode('utf-8')).hexdigest()[:8], 16)

            candidates.append({
                "media": media,
                "title": clean_title,
                "link": entry.link,
                "canonical_url": canonical_url,
                "published_at": pub_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "summary": summary,
                "score": score_data["total_score"],
                "score_breakdown": score_data,
                "_tie_breaker": (score_data["total_score"], pub_date.timestamp(), title_hash)
            })

        # Deterministic ranking: highest score -> newest timestamp -> title hash
        candidates.sort(key=lambda x: (x["score"], x["_tie_breaker"][1], x["_tie_breaker"][2]), reverse=True)

        # Retain up to CANDIDATES_PER_PUBLISHER (default 20)
        selected_pool = candidates[:CANDIDATES_PER_PUBLISHER]
        all_publisher_candidates[media] = selected_pool

        diagnostic_stats[media] = {
            "status": "success" if len(selected_pool) >= ARTICLES_PER_PUBLISHER else "shortage",
            "raw_count": len(raw_entries),
            "eligible_count": len(candidates),
            "selected_count": min(len(selected_pool), ARTICLES_PER_PUBLISHER)
        }

        print(f" -> Ranked {len(candidates)} eligible candidates. Bounded pool size: {len(selected_pool)}.")
        for idx, item in enumerate(selected_pool[:ARTICLES_PER_PUBLISHER]):
            print(f"    [Top {idx+1}] Score {item['score']} | {item['title'][:65]}")

        # Jitter delay between publishers to prevent triggering WAF burst limits
        time.sleep(2.0 + random.uniform(0.5, 1.0))

    # Flatten candidates for serialization while marking primary vs backup
    serialized_articles = []
    for media, pool in all_publisher_candidates.items():
        for rank, item in enumerate(pool):
            article_copy = dict(item)
            article_copy.pop("_tie_breaker", None)
            article_copy["rank"] = rank + 1
            article_copy["is_primary"] = (rank < ARTICLES_PER_PUBLISHER)
            serialized_articles.append(article_copy)

    # Strict validation: If 0 articles fetched across all sources, do NOT inject dummy/mock data.
    # Raise an explicit RuntimeError to prevent publishing stale or fabricated newsletters.
    if len(serialized_articles) == 0:
        error_msg = "[Fatal Ingestion Error] 0 articles fetched across all media sources. Aborting pipeline."
        print(f"\n{error_msg}", file=sys.stderr)
        raise RuntimeError(error_msg)

    os.makedirs("src", exist_ok=True)
    with open("src/articles.json", "w", encoding="utf-8") as f:
        json.dump(serialized_articles, f, ensure_ascii=False, indent=2)

    with open("src/fetcher_stats.json", "w", encoding="utf-8") as f:
        json.dump(diagnostic_stats, f, ensure_ascii=False, indent=2)

    primary_count = sum(1 for a in serialized_articles if a.get("is_primary"))
    print(f"\nSuccessfully serialized {len(serialized_articles)} candidates ({primary_count} primary targets) to src/articles.json.")
    return serialized_articles

if __name__ == "__main__":
    fetch_latest_articles()
