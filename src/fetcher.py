import feedparser
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

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
    articles = []
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    for media, url in TARGET_FEEDS.items():
        print(f"Fetching {media}...")
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            # Parse published date
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                
                # Filter articles from the last 24 hours
                if pub_date > twenty_four_hours_ago:
                    summary = clean_html(entry.summary if hasattr(entry, 'summary') else "")
                    articles.append({
                        "media": media,
                        "title": entry.title,
                        "link": entry.link,
                        "published_at": pub_date.isoformat(),
                        "summary": summary
                    })
    
    # Save payload for Milestone 2 (LLM Integration)
    with open("src/articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Successfully fetched {len(articles)} articles.")

if __name__ == "__main__":
    fetch_latest_articles()
