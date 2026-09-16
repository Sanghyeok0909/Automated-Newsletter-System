import requests
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

def fetch_latest_articles():
    all_articles = []
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    for media, url in TARGET_FEEDS.items():
        print(f"Fetching {media} via RSS Proxy...")
        # 무료 공용 Proxy API를 경유하여 방화벽 원천 차단 우회
        api_url = f"https://api.rss2json.com/v1/api.json?rss_url={url}"
        
        try:
            response = requests.get(api_url, timeout=15)
            data = response.json()
            
            if data.get('status') == 'ok':
                media_articles = []
                for item in data.get('items', []):
                    pubDate_str = item.get('pubDate')
                    if pubDate_str:
                        try:
                            pub_date = datetime.strptime(pubDate_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            pub_date = datetime.utcnow()
                            
                        if pub_date > twenty_four_hours_ago:
                            soup = BeautifulSoup(item.get('description', ''), "html.parser")
                            summary = soup.get_text(separator=" ", strip=True)
                            media_articles.append({
                                "media": media,
                                "title": item.get('title', ''),
                                "link": item.get('link', ''),
                                "published_at": pub_date.isoformat(),
                                "summary": summary
                            })
                # 매체별 최신 기사 2개 큐레이션 유지
                all_articles.extend(media_articles[:2])
        except Exception as e:
            print(f"[Error] Failed to fetch {media}: {e}")
        
        time.sleep(2)
    
    with open("src/articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"Successfully fetched {len(all_articles)} curated articles.")

if __name__ == "__main__":
    fetch_latest_articles()
