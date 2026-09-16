import urllib.request
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

GOOGLE_NEWS_FEEDS = {
    "The Verge": "https://news.google.com/rss/search?q=site:theverge.com+when:1d&hl=en-US&gl=US&ceid=US:en",
    "TechCrunch": "https://news.google.com/rss/search?q=site:techcrunch.com+when:1d&hl=en-US&gl=US&ceid=US:en",
    "Ars Technica": "https://news.google.com/rss/search?q=site:arstechnica.com+when:1d&hl=en-US&gl=US&ceid=US:en",
    "MIT Tech Review": "https://news.google.com/rss/search?q=site:technologyreview.com+when:1d&hl=en-US&gl=US&ceid=US:en",
    "The Information": "https://news.google.com/rss/search?q=site:theinformation.com+when:1d&hl=en-US&gl=US&ceid=US:en"
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/xml, text/xml, */*'
}

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def fetch_xml_data(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read()
    except Exception as e:
        print(f" -> Network Fetch Failed: {e}")
        return None

def fetch_latest_articles():
    all_articles = []
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    for media, direct_url in TARGET_FEEDS.items():
        print(f"Attempting to fetch {media}...")
        
        # Tier 1: 직접 RSS 접근 시도
        xml_data = fetch_xml_data(direct_url)
        
        # Tier 2: 실패 시 Google News로 즉각 폴백(Fallback) 우회
        if not xml_data or b'<rss' not in xml_data.lower() and b'<feed' not in xml_data.lower():
            print(f" -> Direct access blocked by Cloudflare. Falling back to Google News...")
            xml_data = fetch_xml_data(GOOGLE_NEWS_FEEDS[media])

        if not xml_data:
            print(f" -> [Critical] Both methods failed for {media}. Skipping.")
            continue

        feed = feedparser.parse(xml_data)
        media_articles = []
        
        for entry in feed.entries:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                if pub_date > twenty_four_hours_ago:
                    summary = clean_html(entry.summary if hasattr(entry, 'summary') else "")
                    clean_title = entry.title.split(' - ')[0] if ' - ' in entry.title else entry.title
                    
                    media_articles.append({
                        "media": media,
                        "title": clean_title,
                        "link": entry.link,
                        "published_at": pub_date.isoformat(),
                        "summary": summary
                    })
                    
        if media_articles:
            all_articles.extend(media_articles[:2])
            print(f" -> Success! Extracted {len(media_articles[:2])} valid articles.")
        
        time.sleep(2)

    # [핵심] 긴급 프로토콜: 0건 수집 시 조용한 스킵(Silent Skip)을 막기 위해 가짜 데이터 주입하여 파이프라인 강제 실행
    if len(all_articles) == 0:
        print("\n[EMERGENCY] 0 articles fetched. Injecting Diagnostic Artifact to force pipeline execution and Git commit.")
        all_articles.append({
            "media": "System Diagnostic",
            "title": "Zero-Capital Pipeline Connection Status",
            "link": "https://github.com",
            "published_at": datetime.utcnow().isoformat(),
            "summary": "This is an automated diagnostic artifact. If you are reading this in the generated newsletter, it means all external fetches were temporarily blocked, but the CI/CD pipeline, LLM connection, and Git push mechanics are functioning perfectly."
        })

    with open("src/articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"\nSuccessfully serialized {len(all_articles)} articles for the analyzer.")

if __name__ == "__main__":
    fetch_latest_articles()
