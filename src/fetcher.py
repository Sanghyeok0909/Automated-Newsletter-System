import feedparser
import requests
import json
import time
import urllib.parse
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

    for media, url in TARGET_FEEDS.items():
        print(f"Fetching {media} via AllOrigins Proxy...")
        # URL 인코딩을 적용하여 AllOrigins 프록시 우회 요청
        encoded_url = urllib.parse.quote(url, safe='')
        proxy_url = f"https://api.allorigins.win/raw?url={encoded_url}"
        
        try:
            # 브라우저 위장 헤더 추가
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(proxy_url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                # 반환된 순수 XML 원본을 feedparser로 로컬에서 직접 해독
                feed = feedparser.parse(response.content)
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
                # 매체별 최신 기사 딱 2개씩만 큐레이션 (총 10개 유지)
                all_articles.extend(media_articles[:2])
                print(f" -> Found {len(media_articles[:2])} valid articles.")
            else:
                print(f"[Error] Proxy returned HTTP {response.status_code} for {media}")
        except Exception as e:
            print(f"[Error] Failed to fetch {media}: {e}")
        
        # 프록시 서버 과부하 방지 딜레이
        time.sleep(3)
    
    with open("src/articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"Successfully fetched {len(all_articles)} curated articles.")

if __name__ == "__main__":
    fetch_latest_articles()
