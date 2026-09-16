import feedparser
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# [핵심 리팩토링] Google News RSS 검색 쿼리를 활용한 우회 (site:도메인 + when:1d)
TARGET_FEEDS = {
    "The Verge": "https://news.google.com/rss/search?q=site:theverge.com+when:1d&hl=en-US&gl=US&ceid=US:en",
    "TechCrunch": "https://news.google.com/rss/search?q=site:techcrunch.com+when:1d&hl=en-US&gl=US&ceid=US:en",
    "Ars Technica": "https://news.google.com/rss/search?q=site:arstechnica.com+when:1d&hl=en-US&gl=US&ceid=US:en",
    "MIT Tech Review": "https://news.google.com/rss/search?q=site:technologyreview.com+when:1d&hl=en-US&gl=US&ceid=US:en",
    "The Information": "https://news.google.com/rss/search?q=site:theinformation.com+when:1d&hl=en-US&gl=US&ceid=US:en"
}

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def fetch_latest_articles():
    all_articles = []
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    for media, url in TARGET_FEEDS.items():
        print(f"Fetching {media} via Google News Aggregator...")
        try:
            # Google News는 데이터센터 IP를 차단하지 않으므로 순수 feedparser로 직접 해독 가능
            feed = feedparser.parse(url)
            media_articles = []
            
            for entry in feed.entries:
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    if pub_date > twenty_four_hours_ago:
                        summary = clean_html(entry.summary if hasattr(entry, 'summary') else "")
                        # Google News 제목 포맷팅 정리
                        clean_title = entry.title.split(' - ')[0] if ' - ' in entry.title else entry.title
                        
                        media_articles.append({
                            "media": media,
                            "title": clean_title,
                            "link": entry.link,
                            "published_at": pub_date.isoformat(),
                            "summary": summary
                        })
                        
            # 매체별 최신 기사 2개 큐레이션 (총 10개)
            all_articles.extend(media_articles[:2])
            print(f" -> Found {len(media_articles[:2])} valid articles.")
        except Exception as e:
            print(f"[Error] Failed to fetch {media}: {e}")
        
        time.sleep(2)
    
    with open("src/articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"Successfully fetched {len(all_articles)} curated articles.")

if __name__ == "__main__":
    fetch_latest_articles()
