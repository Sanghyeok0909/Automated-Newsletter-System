import cloudscraper
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
    all_articles = []
    # 안전한 시간 비교를 위해 UTC 기준 24시간 계산
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    # Cloudscraper를 사용하여 실제 Windows 기반 Chrome 브라우저의 TLS 지문을 완벽히 모방
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    for media, url in TARGET_FEEDS.items():
        print(f"Fetching {media} via Cloudscraper...")
        try:
            # 외부 프록시 없이 직접 접속하여 타임아웃 원천 방지
            response = scraper.get(url, timeout=15)
            
            if response.status_code == 200:
                # 성공적으로 가져온 XML 원문을 feedparser로 해독
                feed = feedparser.parse(response.text)
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
                # 매체별 최신 기사 2개 큐레이션 (총 10개 유지)
                all_articles.extend(media_articles[:2])
                print(f" -> Found {len(media_articles[:2])} valid articles.")
            else:
                print(f"[Error] Server returned HTTP {response.status_code} for {media}")
        except Exception as e:
            print(f"[Error] Failed to fetch {media}: {e}")
        
        # 서버 과부하 방지 네이티브 딜레이
        time.sleep(3)
    
    with open("src/articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"Successfully fetched {len(all_articles)} curated articles.")

if __name__ == "__main__":
    fetch_latest_articles()
