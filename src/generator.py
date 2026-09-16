import json
import os
import sys
from datetime import datetime

def generate_newsletter():
    try:
        with open("src/translated_articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("[Critical Error] translated_articles.json not found. Run analyzer.py first.", file=sys.stderr)
        sys.exit(1)

    # Fail-Fast: If articles array is empty, do not exit silently
    if not articles:
        print("[Critical Error] translated_articles.json is empty. Nothing to publish.", file=sys.stderr)
        sys.exit(1)

    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Build Markdown Format
    md_content = f"# Daily Tech Insights: {today_str}\n\n"
    md_content += "> Curated & Translated by Zero-Capital Autonomous Pipeline\n\n---\n\n"

    # 2. Build HTML Format (For direct Substack paste/API)
    html_content = f"<html><head><meta charset='utf-8'></head><body>\n"
    html_content += f"<h1>Daily Tech Insights: {today_str}</h1>\n"
    html_content += f"<p><em>Curated & Translated by Zero-Capital Autonomous Pipeline</em></p><hr>\n"

    for article in articles:
        # LLM 아웃풋 키 매핑 (에러 방지용 dict.get 사용)
        k_title = article.get("korean_title", article["title"])
        k_summary = article.get("summary_3_lines", [])
        insight = article.get("business_insight", "인사이트를 추출할 수 없습니다.")
        link = article["link"]
        media = article["media"]

        # Append to Markdown
        md_content += f"## {k_title}\n"
        md_content += f"**Source:** [{media}]({link})\n\n"
        md_content += "**핵심 요약:**\n"
        if isinstance(k_summary, list):
            for line in k_summary:
                md_content += f"- {line}\n"
        md_content += f"\n**💡 비즈니스 인사이트:** {insight}\n\n---\n\n"

        # Append to HTML
        html_content += f"<h2>{k_title}</h2>\n"
        html_content += f"<p><strong>Source:</strong> <a href='{link}'>{media}</a></p>\n"
        html_content += "<ul>\n"
        if isinstance(k_summary, list):
            for line in k_summary:
                html_content += f"<li>{line}</li>\n"
        html_content += "</ul>\n"
        html_content += f"<p><strong>💡 비즈니스 인사이트:</strong> {insight}</p>\n<hr>\n"

    html_content += "</body></html>"

    # Create output directory
    os.makedirs("dist", exist_ok=True)
    
    md_path = f"dist/newsletter-{today_str}.md"
    html_path = f"dist/newsletter-{today_str}.html"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Sanity Check
    if not os.path.exists(md_path) or os.path.getsize(md_path) == 0:
        print(f"[Critical Error] Failed to write {md_path}.", file=sys.stderr)
        sys.exit(1)

    print(f"\n[Success] Newsletter generated successfully!")
    print(f"- Markdown: {md_path}")
    print(f"- HTML: {html_path}")

if __name__ == "__main__":
    generate_newsletter()
