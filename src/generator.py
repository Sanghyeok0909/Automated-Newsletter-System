import json
import os
import sys
from datetime import datetime
from html import escape as html_escape

def render_html_template(articles, today_str):
    """
    모바일 퍼스트 및 프리미엄 미니멀리즘 디자인 시스템이 적용된
    자가완결형(Self-contained) HTML 뉴스레터 템플릿 렌더링
    """
    article_cards = []
    for article in articles:
        k_title = article.get("korean_title", article.get("title", "제목 없음"))
        k_summary = article.get("summary_3_lines", [])
        insight = article.get("business_insight", "인사이트를 추출할 수 없습니다.")
        link = article.get("link", "#")
        media = article.get("media", "Tech Media")

        # 요약 리스트 항목 렌더링
        summary_items = ""
        if isinstance(k_summary, list):
            for item in k_summary:
                summary_items += f"          <li>{html_escape(str(item))}</li>\n"
        elif isinstance(k_summary, str):
            summary_items += f"          <li>{html_escape(k_summary)}</li>\n"

        card_html = f"""      <!-- Article Card -->
      <article class="article-card">
        <header class="card-header">
          <div class="meta-row">
            <span class="media-tag">{html_escape(media)}</span>
            <a href="{link}" target="_blank" rel="noopener noreferrer" class="source-link">원문 읽기 ↗</a>
          </div>
          <h2 class="card-title">{html_escape(k_title)}</h2>
        </header>
        
        <div class="summary-section">
          <h3 class="summary-heading">핵심 요약</h3>
          <ul class="summary-list">
{summary_items}          </ul>
        </div>

        <div class="insight-callout">
          <div class="insight-label">💡 비즈니스 인사이트</div>
          <p class="insight-text">{html_escape(insight)}</p>
        </div>
      </article>"""
        article_cards.append(card_html)

    cards_html_content = "\n\n".join(article_cards)

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Daily Tech Insights: {today_str} - 글로벌 5대 테크 미디어 핵심 요약 및 비즈니스 인사이트">
  <title>Daily Tech Insights: {today_str}</title>
  <style>
    /* ==========================================================================
       Zero-Capital Tech Newsletter - Modern Mobile-First Design System
       Pure CSS / Zero External Network Latency / Fully Self-Contained
       ========================================================================== */
    :root {{
      --bg-page: #f8f9fa;
      --bg-card: #ffffff;
      --bg-subtle: #f1f5f9;
      --bg-insight: #eff6ff;
      --border-insight: #2563eb;
      
      --text-primary: #1e293b;
      --text-secondary: #475569;
      --text-muted: #64748b;
      
      --border-card: #e2e8f0;
      --accent-color: #2563eb;
      --accent-hover: #1d4ed8;
      
      --font-stack: -apple-system, BlinkMacSystemFont, "Pretendard Variable", Pretendard, "Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --container-max: 680px;
      --radius-sm: 6px;
      --radius-md: 12px;
    }}

    /* Night & Early-Morning Eye Protection (Auto Dark Mode) */
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg-page: #0f172a;
        --bg-card: #1e293b;
        --bg-subtle: #334155;
        --bg-insight: #172554;
        --border-insight: #60a5fa;
        
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        
        --border-card: #334155;
        --accent-color: #60a5fa;
        --accent-hover: #93c5fd;
      }}
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html {{
      font-size: 16px;
      -webkit-text-size-adjust: 100%;
      scroll-behavior: smooth;
    }}

    body {{
      font-family: var(--font-stack);
      background-color: var(--bg-page);
      color: var(--text-primary);
      line-height: 1.7;
      word-break: keep-all;
      overflow-wrap: break-word;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    .container {{
      width: 100%;
      max-width: var(--container-max);
      margin: 0 auto;
      padding: 1.5rem 1rem 3.5rem 1rem;
    }}

    /* Top Brand Header */
    .site-header {{
      padding: 1rem 0 1.5rem 0;
      border-bottom: 1px solid var(--border-card);
      margin-bottom: 2rem;
    }}

    .brand-tag {{
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--accent-color);
      background-color: var(--bg-subtle);
      padding: 0.2rem 0.55rem;
      border-radius: 9999px;
      margin-bottom: 0.5rem;
    }}

    .site-title {{
      font-size: 1.75rem;
      font-weight: 800;
      letter-spacing: -0.025em;
      color: var(--text-primary);
      line-height: 1.25;
      margin-bottom: 0.35rem;
    }}

    .site-meta {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.88rem;
      color: var(--text-muted);
    }}

    .site-date {{
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }}

    /* Article Stack & Cards */
    .articles-container {{
      display: flex;
      flex-direction: column;
      gap: 1.75rem;
    }}

    .article-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-md);
      padding: 1.35rem 1.15rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}

    .card-header {{
      margin-bottom: 0.85rem;
    }}

    .meta-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }}

    .media-tag {{
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-secondary);
      background-color: var(--bg-subtle);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-sm);
      padding: 0.15rem 0.45rem;
    }}

    .source-link {{
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--accent-color);
      text-decoration: none;
      transition: color 0.15s ease;
    }}

    .source-link:hover {{
      text-decoration: underline;
      color: var(--accent-hover);
    }}

    .card-title {{
      font-size: 1.25rem;
      font-weight: 700;
      line-height: 1.4;
      letter-spacing: -0.015em;
      color: var(--text-primary);
    }}

    /* Summary Bullets */
    .summary-section {{
      margin-bottom: 0.95rem;
    }}

    .summary-heading {{
      font-size: 0.82rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-muted);
      margin-bottom: 0.35rem;
    }}

    .summary-list {{
      list-style: none;
      padding-left: 0;
    }}

    .summary-list li {{
      position: relative;
      padding-left: 1.1rem;
      margin-bottom: 0.45rem;
      font-size: 0.94rem;
      color: var(--text-secondary);
      line-height: 1.65;
    }}

    .summary-list li::before {{
      content: "•";
      position: absolute;
      left: 0.15rem;
      color: var(--accent-color);
      font-weight: bold;
    }}

    /* Business Insight Callout */
    .insight-callout {{
      background-color: var(--bg-insight);
      border-left: 3.5px solid var(--border-insight);
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      padding: 0.85rem 1rem;
      margin-top: 0.5rem;
    }}

    .insight-label {{
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--accent-color);
      margin-bottom: 0.25rem;
      letter-spacing: -0.01em;
    }}

    .insight-text {{
      font-size: 0.91rem;
      font-weight: 500;
      color: var(--text-primary);
      line-height: 1.6;
    }}

    /* Footer */
    .site-footer {{
      margin-top: 3rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border-card);
      text-align: center;
      font-size: 0.82rem;
      color: var(--text-muted);
      line-height: 1.6;
    }}

    @media (min-width: 640px) {{
      .container {{
        padding: 2.5rem 1.5rem 4rem 1.5rem;
      }}
      .site-title {{
        font-size: 2.1rem;
      }}
      .article-card {{
        padding: 1.5rem;
      }}
      .card-title {{
        font-size: 1.35rem;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header class="site-header">
      <span class="brand-tag">Zero-Capital Autonomous Pipeline</span>
      <h1 class="site-title">Daily Tech Insights</h1>
      <div class="site-meta">
        <time class="site-date">{today_str}</time>
        <span>· 글로벌 5대 테크 미디어 핵심 브리핑</span>
      </div>
    </header>

    <main class="articles-container">
{cards_html_content}
    </main>

    <footer class="site-footer">
      <p>Curated &amp; Translated by Zero-Capital Autonomous Pipeline</p>
      <p style="margin-top: 0.25rem; opacity: 0.8;">© Daily Tech Insights. All rights reserved.</p>
    </footer>
  </div>
</body>
</html>"""
    return full_html

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
    
    # 1. Build Markdown Format (Preserved for archives / Substack)
    md_content = f"# Daily Tech Insights: {today_str}\n\n"
    md_content += "> Curated & Translated by Zero-Capital Autonomous Pipeline\n\n---\n\n"

    for article in articles:
        k_title = article.get("korean_title", article["title"])
        k_summary = article.get("summary_3_lines", [])
        insight = article.get("business_insight", "인사이트를 추출할 수 없습니다.")
        link = article["link"]
        media = article["media"]

        md_content += f"## {k_title}\n"
        md_content += f"**Source:** [{media}]({link})\n\n"
        md_content += "**핵심 요약:**\n"
        if isinstance(k_summary, list):
            for line in k_summary:
                md_content += f"- {line}\n"
        md_content += f"\n**💡 비즈니스 인사이트:** {insight}\n\n---\n\n"

    # 2. Build High-Quality Responsive HTML
    html_content = render_html_template(articles, today_str)

    # Create output directory
    os.makedirs("dist", exist_ok=True)
    
    md_path = f"dist/newsletter-{today_str}.md"
    html_path = f"dist/newsletter-{today_str}.html"
    index_path = "dist/index.html"

    # Write Markdown archive
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Write Daily HTML archive
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Write Root Entry Point for GitHub Pages
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Sanity Check
    if not os.path.exists(md_path) or os.path.getsize(md_path) == 0:
        print(f"[Critical Error] Failed to write {md_path}.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(index_path) or os.path.getsize(index_path) == 0:
        print(f"[Critical Error] Failed to write {index_path}.", file=sys.stderr)
        sys.exit(1)

    print(f"\n[Success] Newsletter generated successfully!")
    print(f"- Markdown: {md_path}")
    print(f"- HTML Archive: {html_path}")
    print(f"- Root Web Entry: {index_path}")

if __name__ == "__main__":
    generate_newsletter()
