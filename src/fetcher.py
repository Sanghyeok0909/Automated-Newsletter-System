import feedparser
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# [Patch] User-Agent spoofing to bypass cloud data center firewalls
feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

TARGET_FEEDS = {
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "The Information": "https://www.theinformation.com/feed"
}

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def fetch_latest_articles():
    all_articles = []
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    for media, url in TARGET_FEEDS.items():
        print(f"Fetching {media}...")
        feed = feedparser.parse(url)
        
        media_articles = []
        for entry in feed.entries:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                
                if pub_date > twenty_four_hours_ago:
                    summary = clean_html(entry.summary if hasattr(entry, 'summary') else "")
                    media_articles.append({
                        "media": media,
                        "title": entry.title,
                        "link": entry.link,
                        "published_at": pub_date.isoformat(),
                        "summary": summary
                    })
        
        # [Patch] Curate strictly top 2 articles per media (Total 10)
        all_articles.extend(media_articles[:2])
        time.sleep(2)
        
    with open("src/articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"Successfully fetched {len(all_articles)} curated articles.")

if __name__ == "__main__":
    fetch_latest_articles()
