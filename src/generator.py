import json
import os
import sys
from datetime import datetime
from html import escape as html_escape

def render_html_template(articles, today_str):
    """
    Discord-inspired macro-navigation & Toss-inspired tactile micro-interaction
    high-density editorial briefing web application.
    Self-contained, zero external runtime dependencies.
    """
    media_brand_map = {
        "The Verge": {"slug": "verge", "mark": "V", "name": "The Verge"},
        "TechCrunch": {"slug": "techcrunch", "mark": "TC", "name": "TechCrunch"},
        "Ars Technica": {"slug": "arstechnica", "mark": "AT", "name": "Ars Technica"},
        "MIT Tech Review": {"slug": "mit", "mark": "MIT", "name": "MIT Tech Review"},
        "The Information": {"slug": "theinformation", "mark": "TI", "name": "The Information"}
    }

    media_counts = {}
    for art in articles:
        m = art.get("media", "Tech Media")
        media_counts[m] = media_counts.get(m, 0) + 1

    # Generate article cards
    article_cards = []
    for idx, article in enumerate(articles):
        k_title = article.get("korean_title", article.get("title", "제목 없음"))
        k_summary = article.get("summary_3_lines", [])
        insight = article.get("business_insight", "인사이트를 추출할 수 없습니다.")
        link = article.get("link", "#")
        media = article.get("media", "Tech Media")
        brand = media_brand_map.get(media, {"slug": "general", "mark": "T", "name": media})
        slug = brand["slug"]
        mark = brand["mark"]

        summary_items = ""
        summary_text_raw = ""
        if isinstance(k_summary, list):
            for item in k_summary:
                summary_items += f'              <li class="summary-bullet">{html_escape(str(item))}</li>\n'
            summary_text_raw = " ".join(str(item) for item in k_summary)
        elif isinstance(k_summary, str):
            summary_items += f'              <li class="summary-bullet">{html_escape(k_summary)}</li>\n'
            summary_text_raw = k_summary

        # Plain search index attribute
        search_blob = f"{k_title} {media} {summary_text_raw} {insight}".lower()
        escaped_search = html_escape(search_blob, quote=True)

        card_html = f"""        <!-- Toss-Style Tactile Article Card -->
        <article class="toss-card" data-media="{slug}" data-search="{escaped_search}" id="article-{idx+1}">
          <div class="card-top-rail">
            <div class="media-identity">
              <span class="media-avatar {slug}" aria-hidden="true">{mark}</span>
              <div class="media-meta">
                <span class="media-name">{html_escape(media)}</span>
                <span class="channel-slug">#{slug}-feed</span>
              </div>
            </div>
            <a href="{link}" target="_blank" rel="noopener noreferrer" class="toss-pill-link" aria-label="{html_escape(k_title)} 원문 기사 열기">
              원문 읽기 ↗
            </a>
          </div>

          <h2 class="card-headline">{html_escape(k_title)}</h2>

          <div class="toss-surface-box">
            <div class="section-badge">핵심 요약</div>
            <ul class="summary-bullet-list">
{summary_items}            </ul>
          </div>

          <div class="toss-insight-card">
            <div class="insight-pill">
              <span class="insight-icon" aria-hidden="true">💡</span>
              <span class="insight-tag">AI 비즈니스 인사이트</span>
            </div>
            <p class="insight-description">{html_escape(insight)}</p>
          </div>

          <div class="card-footer-action">
            <button type="button" class="toss-secondary-btn copy-btn" onclick="copyArticleLink('{link}', this)" aria-label="원문 기사 링크 복사">
              🔗 링크 복사
            </button>
            <span class="reading-time">소요시간 약 45초 (예상)</span>
          </div>
        </article>"""
        article_cards.append(card_html)

    cards_html_content = "\n\n".join(article_cards)

    # Dynamic publisher channels in sidebar
    monitored_sources = [
        ("The Verge", "verge"),
        ("TechCrunch", "techcrunch"),
        ("Ars Technica", "arstechnica"),
        ("MIT Tech Review", "mit"),
        ("The Information", "theinformation")
    ]

    channel_items = []
    for s_name, s_slug in monitored_sources:
        cnt = media_counts.get(s_name, 0)
        mark = media_brand_map[s_name]["mark"]
        channel_items.append(f"""        <button type="button" class="channel-item" data-channel="{s_slug}" onclick="filterFeed('{s_slug}', this)">
          <div class="channel-left">
            <span class="channel-mark-badge {s_slug}">{mark}</span>
            <span class="channel-name">{html_escape(s_name)}</span>
          </div>
          <span class="channel-count" id="channel-count-{s_slug}">{cnt}</span>
        </button>""")
    channel_items_html = "\n".join(channel_items)

    # Dynamic metadata source items
    source_status_items = []
    for s_name, s_slug in monitored_sources:
        cnt = media_counts.get(s_name, 0)
        if cnt > 0:
            badge = f'<span class="status-badge-active" title="{cnt}건 수집 완료">{cnt}건 정상 🟢</span>'
        else:
            badge = '<span class="status-badge-warning" title="수집된 기사 없음">0건 누락/경고 🟡</span>'
        source_status_items.append(f"""      <div class="feed-status-item">
        <span class="status-source-name">{html_escape(s_name)}</span>
        {badge}
      </div>""")
    source_status_html = "\n".join(source_status_items)

    full_html = f"""<!DOCTYPE html>
<html lang="ko" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <meta name="description" content="Daily Tech Insights: {today_str} - 글로벌 5대 테크 미디어 핵심 큐레이션 및 AI 비즈니스 인사이트">
  <title>Daily Tech Insights | {today_str}</title>
  <style>
    /* ==========================================================================
       Design System Tokens (Discord Macro-Structure + Toss Tactile Clarity)
       Pure Vanilla CSS3 / Zero Dependencies / High Accessibility
       ========================================================================== */
    :root {{
      --toss-blue: #3182f6;
      --toss-blue-hover: #1b64da;
      --toss-blue-subtle: rgba(49, 130, 246, 0.12);
      --toss-blue-glow: rgba(49, 130, 246, 0.28);

      --rail-width: 58px;
      --sidebar-width: 232px;
      --metadata-width: 260px;
      --content-max-width: 860px;

      /* Dark Theme (Default) */
      --bg-app: #141518;
      --bg-rail: #191a1d;
      --bg-sidebar: #1e2024;
      --bg-workspace: #25272c;
      --surface-card: #2c2e35;
      --surface-inset: #1a1b1f;
      --surface-hover: #34373f;
      --surface-active: #3c4049;

      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-strong: rgba(255, 255, 255, 0.14);
      --border-focus: rgba(49, 130, 246, 0.6);

      --text-header: #f3f5f8;
      --text-normal: #d1d5dd;
      --text-muted: #8c93a0;
      --text-link: #4593fc;

      --shadow-card: 0 4px 18px rgba(0, 0, 0, 0.22);
      --shadow-hover: 0 10px 32px rgba(0, 0, 0, 0.36);

      --radius-card: 20px;
      --radius-md: 14px;
      --radius-sm: 10px;
      --radius-pill: 9999px;

      --font-stack: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
      --spring-physics: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      --spring-tap: transform 0.12s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    [data-theme="light"] {{
      --bg-app: #f2f4f7;
      --bg-rail: #e4e7ed;
      --bg-sidebar: #edf0f5;
      --bg-workspace: #f8f9fb;
      --surface-card: #ffffff;
      --surface-inset: #f2f4f7;
      --surface-hover: #e6ebf2;
      --surface-active: #dbe1eb;

      --border-subtle: rgba(0, 0, 0, 0.07);
      --border-strong: rgba(0, 0, 0, 0.13);
      --border-focus: rgba(49, 130, 246, 0.7);

      --text-header: #191f28;
      --text-normal: #333d4b;
      --text-muted: #6b7684;
      --text-link: #3182f6;

      --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.06);
      --shadow-hover: 0 8px 26px rgba(0, 0, 0, 0.12);
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
    }}

    html, body {{
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      font-family: var(--font-stack);
      background-color: var(--bg-app);
      color: var(--text-normal);
      line-height: 1.6;
      word-break: keep-all;
      -webkit-font-smoothing: antialiased;
    }}

    /* Global App Shell Layout */
    .discord-app-shell {{
      display: flex;
      width: 100%;
      height: 100%;
      position: relative;
    }}

    /* ==========================================================================
       Level 1: Global Rail (Streamlined Brand Home Control)
       ========================================================================== */
    .global-rail {{
      width: var(--rail-width);
      min-width: var(--rail-width);
      height: 100%;
      background-color: var(--bg-rail);
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 14px 0;
      border-right: 1px solid var(--border-subtle);
      z-index: 30;
      flex-shrink: 0;
    }}

    .rail-btn {{
      position: relative;
      width: 42px;
      height: 42px;
      border-radius: 14px;
      background-color: var(--toss-blue);
      color: #ffffff;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      transition: var(--spring-physics);
      box-shadow: 0 4px 14px var(--toss-blue-glow);
    }}

    .rail-btn:hover {{
      transform: scale(1.06);
      background-color: var(--toss-blue-hover);
    }}

    .rail-btn:active {{
      transform: scale(0.94);
    }}

    .rail-btn:focus-visible {{
      outline: 2px solid #ffffff;
      outline-offset: 2px;
    }}

    .rail-btn.active::before {{
      content: "";
      position: absolute;
      left: -8px;
      width: 4px;
      height: 28px;
      border-radius: 0 4px 4px 0;
      background-color: #ffffff;
    }}

    /* ==========================================================================
       Level 2: Context Sidebar (Search + Channels Navigation)
       ========================================================================== */
    .context-sidebar {{
      width: var(--sidebar-width);
      min-width: var(--sidebar-width);
      height: 100%;
      background-color: var(--bg-sidebar);
      display: flex;
      flex-direction: column;
      border-right: 1px solid var(--border-subtle);
      z-index: 25;
      flex-shrink: 0;
      transition: transform 0.24s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .server-header {{
      height: 52px;
      padding: 0 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-subtle);
      font-weight: 800;
      font-size: 0.95rem;
      color: var(--text-header);
    }}

    .server-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    /* Sidebar Search Input */
    .sidebar-search-box {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--border-subtle);
    }}

    .search-input-wrapper {{
      position: relative;
      display: flex;
      align-items: center;
      width: 100%;
    }}

    .search-icon {{
      position: absolute;
      left: 10px;
      font-size: 0.8rem;
      color: var(--text-muted);
      pointer-events: none;
    }}

    .toss-search-input {{
      width: 100%;
      height: 34px;
      padding: 0 28px 0 28px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background-color: var(--surface-inset);
      color: var(--text-header);
      font-size: 0.82rem;
      font-family: inherit;
      outline: none;
      transition: var(--spring-physics);
    }}

    .toss-search-input:focus {{
      border-color: var(--border-focus);
      box-shadow: 0 0 0 2px var(--toss-blue-subtle);
    }}

    .search-clear-btn {{
      position: absolute;
      right: 6px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      border: none;
      background-color: var(--surface-hover);
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.7rem;
      transition: var(--spring-physics);
    }}

    .search-clear-btn:hover {{
      color: var(--text-header);
      background-color: var(--surface-active);
    }}

    .channels-scroll {{
      flex: 1;
      overflow-y: auto;
      padding: 10px 8px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .channel-category {{
      font-size: 0.72rem;
      font-weight: 800;
      letter-spacing: 0.04em;
      color: var(--text-muted);
      text-transform: uppercase;
      padding: 10px 8px 4px 8px;
    }}

    .channel-item {{
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 10px;
      border-radius: 10px;
      color: var(--text-muted);
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
      border: none;
      background: transparent;
      transition: var(--spring-physics);
      text-align: left;
      font-family: inherit;
    }}

    .channel-item:hover {{
      background-color: var(--surface-hover);
      color: var(--text-header);
    }}

    .channel-item.active {{
      background-color: var(--surface-active);
      color: var(--text-header);
      font-weight: 700;
    }}

    .channel-item:focus-visible {{
      outline: 2px solid var(--toss-blue);
      outline-offset: 1px;
    }}

    .channel-left {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .channel-mark-badge {{
      width: 22px;
      height: 22px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 0.68rem;
      font-weight: 800;
      color: #ffffff;
      background-color: var(--toss-blue);
    }}
    .channel-mark-badge.all {{ background-color: var(--toss-blue); }}
    .channel-mark-badge.verge {{ background-color: #e0005a; }}
    .channel-mark-badge.techcrunch {{ background-color: #029924; }}
    .channel-mark-badge.arstechnica {{ background-color: #ff4e00; }}
    .channel-mark-badge.mit {{ background-color: #333333; }}
    .channel-mark-badge.theinformation {{ background-color: #0d253f; }}

    .channel-name {{
      font-size: 0.86rem;
      letter-spacing: -0.01em;
    }}

    .channel-count {{
      font-size: 0.72rem;
      background-color: var(--surface-inset);
      padding: 2px 7px;
      border-radius: 10px;
      font-weight: 700;
      color: var(--text-muted);
    }}

    .channel-item.active .channel-count {{
      color: var(--text-header);
      background-color: var(--surface-card);
    }}

    .sidebar-user-tray {{
      height: 52px;
      background-color: var(--bg-rail);
      padding: 0 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-top: 1px solid var(--border-subtle);
    }}

    .user-info-box {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .status-dot {{
      width: 9px;
      height: 9px;
      background-color: #23a55a;
      border-radius: 50%;
      box-shadow: 0 0 6px #23a55a;
    }}

    .user-name-label {{
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--text-header);
      line-height: 1.2;
    }}

    .user-sub-label {{
      font-size: 0.68rem;
      color: var(--text-muted);
    }}

    /* ==========================================================================
       Level 3: Primary Workspace (Briefing Header + Article Cards)
       ========================================================================== */
    .chat-workspace {{
      flex: 1;
      height: 100%;
      display: flex;
      flex-direction: column;
      background-color: var(--bg-workspace);
      overflow: hidden;
      position: relative;
    }}

    .workspace-header {{
      height: 52px;
      padding: 0 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-subtle);
      background-color: var(--bg-workspace);
      z-index: 15;
      flex-shrink: 0;
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .mobile-menu-btn {{
      display: none;
      width: 36px;
      height: 36px;
      border-radius: 10px;
      border: 1px solid var(--border-subtle);
      background-color: var(--surface-card);
      color: var(--text-header);
      cursor: pointer;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
    }}

    .topic-pill {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
      font-size: 0.95rem;
      color: var(--text-header);
    }}

    .topic-divider {{
      width: 1px;
      height: 14px;
      background-color: var(--border-strong);
    }}

    .topic-desc {{
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--text-muted);
    }}

    .header-controls {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .theme-toggle-btn {{
      padding: 6px 12px;
      border-radius: 10px;
      background-color: var(--surface-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-normal);
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      transition: var(--spring-physics);
      font-family: inherit;
    }}

    .theme-toggle-btn:hover {{
      background-color: var(--surface-hover);
      transform: translateY(-1px);
    }}

    .theme-toggle-btn:focus-visible {{
      outline: 2px solid var(--toss-blue);
      outline-offset: 1px;
    }}

    /* Scrollable Feed Container */
    .messages-feed {{
      flex: 1;
      overflow-y: auto;
      padding: 20px 24px 60px 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 18px;
    }}

    /* Streamlined Editorial Briefing Header */
    .feed-hero {{
      width: 100%;
      max-width: var(--content-max-width);
      background: var(--surface-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-card);
      padding: 20px 22px;
      box-shadow: var(--shadow-card);
    }}

    .hero-badge-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
    }}

    .toss-tag {{
      font-size: 0.72rem;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: var(--radius-pill);
      background-color: var(--toss-blue-subtle);
      color: var(--toss-blue);
      letter-spacing: 0.02em;
    }}

    .hero-date-badge {{
      font-size: 0.78rem;
      color: var(--text-muted);
      font-weight: 700;
    }}

    .hero-count-badge {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 600;
      margin-left: auto;
    }}

    .hero-title {{
      font-size: 1.55rem;
      font-weight: 900;
      letter-spacing: -0.03em;
      color: var(--text-header);
      margin-bottom: 6px;
      line-height: 1.25;
    }}

    .hero-subtitle {{
      font-size: 0.9rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    /* ==========================================================================
       Toss Article Cards (Clean Hierarchy & Typography)
       ========================================================================== */
    .toss-card {{
      width: 100%;
      max-width: var(--content-max-width);
      background-color: var(--surface-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-card);
      padding: 22px 24px;
      box-shadow: var(--shadow-card);
      transition: var(--spring-physics);
      display: flex;
      flex-direction: column;
      gap: 15px;
    }}

    .toss-card:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-hover);
      border-color: var(--border-strong);
    }}

    .card-top-rail {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .media-identity {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .media-avatar {{
      width: 32px;
      height: 32px;
      border-radius: 9px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      color: #ffffff;
      font-size: 0.76rem;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
      flex-shrink: 0;
    }}
    .media-avatar.verge {{ background: linear-gradient(135deg, #e0005a, #fa2d60); }}
    .media-avatar.techcrunch {{ background: linear-gradient(135deg, #029924, #00d235); }}
    .media-avatar.arstechnica {{ background: linear-gradient(135deg, #ff4e00, #ff8100); }}
    .media-avatar.mit {{ background: linear-gradient(135deg, #222222, #444444); }}
    .media-avatar.theinformation {{ background: linear-gradient(135deg, #0d253f, #1b497a); }}

    .media-name {{
      font-size: 0.9rem;
      font-weight: 800;
      color: var(--text-header);
    }}

    .channel-slug {{
      display: block;
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-muted);
    }}

    .toss-pill-link {{
      font-size: 0.8rem;
      font-weight: 800;
      padding: 6px 14px;
      border-radius: var(--radius-pill);
      background-color: var(--toss-blue-subtle);
      color: var(--toss-blue);
      text-decoration: none;
      transition: var(--spring-physics);
      display: inline-flex;
      align-items: center;
    }}

    .toss-pill-link:hover {{
      background-color: var(--toss-blue);
      color: #ffffff;
      transform: scale(1.03);
    }}

    .toss-pill-link:focus-visible {{
      outline: 2px solid var(--toss-blue);
      outline-offset: 2px;
    }}

    .card-headline {{
      font-size: 1.3rem;
      font-weight: 800;
      letter-spacing: -0.025em;
      color: var(--text-header);
      line-height: 1.4;
    }}

    /* Inset Summary Box */
    .toss-surface-box {{
      background-color: var(--surface-inset);
      border-radius: var(--radius-sm);
      padding: 14px 16px;
      border: 1px solid var(--border-subtle);
    }}

    .section-badge {{
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-muted);
      margin-bottom: 8px;
    }}

    .summary-bullet-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 7px;
    }}

    .summary-bullet {{
      position: relative;
      padding-left: 16px;
      font-size: 0.92rem;
      color: var(--text-normal);
      line-height: 1.58;
    }}

    .summary-bullet::before {{
      content: "•";
      position: absolute;
      left: 2px;
      color: var(--toss-blue);
      font-weight: 900;
      font-size: 1.15rem;
      line-height: 1;
    }}

    /* AI Business Insight Callout */
    .toss-insight-card {{
      background-color: var(--toss-blue-subtle);
      border-left: 3px solid var(--toss-blue);
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      padding: 12px 16px;
    }}

    .insight-pill {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.78rem;
      font-weight: 800;
      color: var(--toss-blue);
      margin-bottom: 6px;
    }}

    .insight-description {{
      font-size: 0.91rem;
      font-weight: 600;
      color: var(--text-header);
      line-height: 1.58;
    }}

    .card-footer-action {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 2px;
    }}

    .toss-secondary-btn {{
      border: 1px solid var(--border-subtle);
      background-color: var(--surface-inset);
      color: var(--text-muted);
      font-size: 0.8rem;
      font-weight: 700;
      padding: 6px 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: var(--spring-physics);
      font-family: inherit;
    }}

    .toss-secondary-btn:hover {{
      background-color: var(--surface-hover);
      color: var(--text-header);
    }}

    .toss-secondary-btn.copied {{
      background-color: var(--toss-blue);
      color: #ffffff;
      border-color: var(--toss-blue);
    }}

    .reading-time {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 600;
    }}

    /* No-Results State */
    .toss-empty-state {{
      width: 100%;
      max-width: var(--content-max-width);
      background-color: var(--surface-card);
      border: 1px dashed var(--border-strong);
      border-radius: var(--radius-card);
      padding: 48px 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      gap: 12px;
    }}

    .empty-icon {{
      font-size: 2.2rem;
      opacity: 0.8;
    }}

    .empty-title {{
      font-size: 1.15rem;
      font-weight: 800;
      color: var(--text-header);
    }}

    .empty-desc {{
      font-size: 0.86rem;
      color: var(--text-muted);
      margin-bottom: 6px;
    }}

    /* ==========================================================================
       Level 4: Metadata Panel (System Indicators & Publisher Status)
       ========================================================================== */
    .metadata-panel {{
      width: var(--metadata-width);
      min-width: var(--metadata-width);
      height: 100%;
      background-color: var(--bg-sidebar);
      border-left: 1px solid var(--border-subtle);
      padding: 16px 14px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      overflow-y: auto;
      flex-shrink: 0;
    }}

    .meta-group-title {{
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 6px;
    }}

    .metric-card {{
      background-color: var(--surface-card);
      border-radius: var(--radius-sm);
      padding: 12px 14px;
      border: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}

    .metric-label {{
      font-size: 0.73rem;
      color: var(--text-muted);
      font-weight: 600;
    }}

    .metric-value {{
      font-size: 1.2rem;
      font-weight: 900;
      color: var(--toss-blue);
      letter-spacing: -0.02em;
    }}

    .metric-subtext {{
      font-size: 0.68rem;
      color: var(--text-muted);
    }}

    .feed-status-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 10px;
      border-radius: 8px;
      background-color: var(--surface-card);
      font-size: 0.78rem;
      font-weight: 700;
      border: 1px solid var(--border-subtle);
    }}

    .status-source-name {{
      color: var(--text-header);
    }}

    .status-badge-active {{
      color: #23a55a;
      font-size: 0.73rem;
    }}

    .status-badge-warning {{
      color: #f59f00;
      font-size: 0.73rem;
      font-weight: 800;
    }}

    /* Toast Notification */
    .toss-toast {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background-color: #191f28;
      color: #ffffff;
      padding: 10px 18px;
      border-radius: var(--radius-pill);
      font-size: 0.85rem;
      font-weight: 700;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
      z-index: 100;
      opacity: 0;
      pointer-events: none;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    [data-theme="light"] .toss-toast {{
      background-color: #333d4b;
    }}

    .toss-toast.show {{
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }}

    /* Drawer Backdrop for Mobile */
    .drawer-backdrop {{
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background-color: rgba(0, 0, 0, 0.45);
      z-index: 24;
      opacity: 0;
      transition: opacity 0.2s ease;
    }}

    /* ==========================================================================
       Responsive Breakpoints
       ========================================================================== */
    @media (max-width: 1180px) {{
      .metadata-panel {{
        display: none;
      }}
    }}

    @media (max-width: 768px) {{
      .global-rail {{
        display: none;
      }}
      .mobile-menu-btn {{
        display: flex;
      }}
      .context-sidebar {{
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        transform: translateX(-100%);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
      }}
      .context-sidebar.open {{
        transform: translateX(0);
      }}
      .drawer-backdrop.open {{
        display: block;
        opacity: 1;
      }}
      .messages-feed {{
        padding: 14px 14px 40px 14px;
        gap: 14px;
      }}
      .feed-hero {{
        padding: 16px 16px;
      }}
      .hero-title {{
        font-size: 1.35rem;
      }}
      .toss-card {{
        padding: 18px 16px;
        border-radius: 16px;
      }}
      .card-headline {{
        font-size: 1.12rem;
      }}
      .topic-desc {{
        display: none;
      }}
    }}

    /* Accessibility: Reduced Motion */
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="discord-app-shell">

    <!-- Level 1: Global Rail (Deterministic Home / Reset Control) -->
    <nav class="global-rail" aria-label="글로벌 홈 네비게이션">
      <button type="button" class="rail-btn active" id="homeRailBtn" title="전체 브리핑 피드 (초기화)" aria-label="전체 브리핑 피드로 이동" onclick="resetAllFilters(this)">
        ⚡
      </button>
    </nav>

    <!-- Mobile Drawer Backdrop -->
    <div class="drawer-backdrop" id="drawerBackdrop" onclick="closeMobileMenu()" aria-hidden="true"></div>

    <!-- Level 2: Context Sidebar (Search + Channels) -->
    <aside class="context-sidebar" aria-label="채널 네비게이션">
      <div class="server-header">
        <span class="server-badge">⚡ Tech Intel HQ</span>
        <span style="font-size: 0.8rem; color: var(--toss-blue);" aria-hidden="true">✔</span>
      </div>

      <!-- Search Input -->
      <div class="sidebar-search-box">
        <div class="search-input-wrapper">
          <span class="search-icon" aria-hidden="true">🔍</span>
          <input
            type="search"
            id="searchInput"
            class="toss-search-input"
            placeholder="기사 및 키워드 검색..."
            aria-label="기사 실시간 검색"
            autocomplete="off"
            oninput="handleSearch(this.value)"
          >
          <button type="button" id="searchClearBtn" class="search-clear-btn" aria-label="검색어 초기화" onclick="clearSearch()" style="display: none;">✕</button>
        </div>
      </div>

      <div class="channels-scroll">
        <div class="channel-category">데일리 피드</div>
        <button type="button" class="channel-item active" data-channel="all" onclick="filterFeed('all', this)">
          <div class="channel-left">
            <span class="channel-mark-badge all">⚡</span>
            <span class="channel-name">오늘의 브리핑</span>
          </div>
          <span class="channel-count">{len(articles)}</span>
        </button>

        <div class="channel-category">타겟 매체 채널</div>
{channel_items_html}
      </div>

      <div class="sidebar-user-tray">
        <div class="user-info-box">
          <div class="status-dot" aria-hidden="true"></div>
          <div>
            <div class="user-name-label">Zero-Capital Agent</div>
            <div class="user-sub-label">GitHub Actions 파이프라인</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Level 3: Primary Workspace -->
    <main class="chat-workspace">
      <header class="workspace-header">
        <div class="header-left">
          <button type="button" class="mobile-menu-btn" id="mobileMenuBtn" aria-label="채널 메뉴 열기" aria-expanded="false" onclick="toggleMobileMenu()">
            ☰
          </button>
          <div class="topic-pill">
            <span id="headerTopicTitle">오늘의 브리핑</span>
            <div class="topic-divider" aria-hidden="true"></div>
            <span class="topic-desc">주요 테크 소식과 비즈니스 시사점을 한눈에.</span>
          </div>
        </div>
        <div class="header-controls">
          <button type="button" class="theme-toggle-btn" onclick="toggleTheme()" id="themeBtn" aria-label="다크/라이트 테마 전환">🌓 테마 전환</button>
        </div>
      </header>

      <section class="messages-feed" id="feedContainer">
        <!-- Editorial Briefing Header -->
        <div class="feed-hero">
          <div class="hero-badge-row">
            <span class="toss-tag">DAILY INTEL</span>
            <span class="hero-date-badge">{today_str}</span>
            <span class="hero-count-badge" id="heroArticleCount">총 {len(articles)}개 기사 큐레이션</span>
          </div>
          <h1 class="hero-title">Daily Tech Insights</h1>
          <p class="hero-subtitle">
            글로벌 5대 테크 미디어의 핵심 보도와 비즈니스 시사점을 AI로 정밀 분석하여 전해드립니다.
          </p>
        </div>

        <!-- No Results Card -->
        <div id="noResultsCard" class="toss-empty-state" style="display: none;">
          <div class="empty-icon" aria-hidden="true">🔍</div>
          <h3 class="empty-title">일치하는 기사가 없습니다</h3>
          <p class="empty-desc">검색어를 변경하거나 선택된 매체 필터를 확인해 주세요.</p>
          <button type="button" class="toss-pill-link" onclick="resetAllFilters()">전체 브리핑 보기</button>
        </div>

{cards_html_content}
      </section>
    </main>

    <!-- Level 4: Metadata Panel (Desktop Right Rail) -->
    <aside class="metadata-panel" aria-label="시스템 지표 패널">
      <div class="meta-group-title">시스템 지표</div>
      <div class="metric-card">
        <span class="metric-label">총 큐레이션 기사</span>
        <span class="metric-value" id="metaVisibleCount">{len(articles)}개</span>
        <span class="metric-subtext">기준 일자: {today_str}</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">인프라 운영 비용</span>
        <span class="metric-value">$0.00</span>
        <span class="metric-subtext">Zero-Capital 무인 아키텍처</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">예상 리딩 소요시간</span>
        <span class="metric-value">약 3분</span>
        <span class="metric-subtext">{len(articles)}개 기사 정독 기준</span>
      </div>

      <div class="meta-group-title">매체별 기사 현황</div>
{source_status_html}
    </aside>

  </div>

  <!-- Toast Notification Container -->
  <div id="tossToast" class="toss-toast" role="status" aria-live="polite">
    원문 기사 링크가 복사되었습니다.
  </div>

  <script>
    // State management
    let activeChannel = 'all';
    let searchQuery = '';

    // Filter & Search composability
    function applyFilters() {{
      const cards = document.querySelectorAll('.toss-card');
      let visibleCount = 0;
      const q = searchQuery.trim().toLowerCase();

      cards.forEach(card => {{
        const mediaSlug = card.getAttribute('data-media');
        const matchesChannel = (activeChannel === 'all' || mediaSlug === activeChannel);

        let matchesQuery = true;
        if (q.length > 0) {{
          const searchData = card.getAttribute('data-search') || '';
          matchesQuery = searchData.includes(q);
        }}

        if (matchesChannel && matchesQuery) {{
          card.style.display = 'flex';
          visibleCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      // Update visible counter
      const visibleCounter = document.getElementById('metaVisibleCount');
      if (visibleCounter) {{
        if (activeChannel === 'all' && q.length === 0) {{
          visibleCounter.textContent = `${{cards.length}}개`;
        }} else {{
          visibleCounter.textContent = `${{visibleCount}}개 / ${{cards.length}}개`;
        }}
      }}

      // Toggle empty state
      const emptyState = document.getElementById('noResultsCard');
      if (emptyState) {{
        emptyState.style.display = visibleCount === 0 ? 'flex' : 'none';
      }}
    }}

    function filterFeed(slug, element) {{
      activeChannel = slug;

      // Update channel active styling
      document.querySelectorAll('.channel-item').forEach(item => item.classList.remove('active'));
      if (element) {{
        element.classList.add('active');
      }} else {{
        const target = document.querySelector(`.channel-item[data-channel="${{slug}}"]`);
        if (target) target.classList.add('active');
      }}

      // Update header topic title
      const topicEl = document.getElementById('headerTopicTitle');
      if (topicEl) {{
        if (slug === 'all') {{
          topicEl.textContent = '오늘의 브리핑';
        }} else {{
          const nameEl = element ? element.querySelector('.channel-name') : null;
          topicEl.textContent = nameEl ? nameEl.textContent : slug;
        }}
      }}

      applyFilters();
      closeMobileMenu();

      // Scroll to top
      const feed = document.getElementById('feedContainer');
      if (feed) feed.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function handleSearch(val) {{
      searchQuery = val;
      const clearBtn = document.getElementById('searchClearBtn');
      if (clearBtn) {{
        clearBtn.style.display = val.length > 0 ? 'flex' : 'none';
      }}
      applyFilters();
    }}

    function clearSearch() {{
      const input = document.getElementById('searchInput');
      if (input) {{
        input.value = '';
        input.focus();
      }}
      handleSearch('');
    }}

    function resetAllFilters(element) {{
      activeChannel = 'all';
      searchQuery = '';
      const input = document.getElementById('searchInput');
      if (input) input.value = '';
      const clearBtn = document.getElementById('searchClearBtn');
      if (clearBtn) clearBtn.style.display = 'none';

      document.querySelectorAll('.channel-item').forEach(item => {{
        if (item.getAttribute('data-channel') === 'all') {{
          item.classList.add('active');
        }} else {{
          item.classList.remove('active');
        }}
      }});

      const topicEl = document.getElementById('headerTopicTitle');
      if (topicEl) topicEl.textContent = '오늘의 브리핑';

      const homeBtn = document.getElementById('homeRailBtn');
      if (homeBtn) homeBtn.classList.add('active');

      applyFilters();
      closeMobileMenu();

      const feed = document.getElementById('feedContainer');
      if (feed) feed.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    // Clipboard & Toast Feedback
    function copyArticleLink(url, btn) {{
      const originalText = btn.innerHTML;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(url).then(() => {{
          showToast('원문 기사 링크가 복사되었습니다.');
          btn.innerHTML = '✓ 복사 완료';
          btn.classList.add('copied');
          setTimeout(() => {{
            btn.innerHTML = originalText;
            btn.classList.remove('copied');
          }}, 2000);
        }}).catch(() => {{
          fallbackCopy(url, btn, originalText);
        }});
      }} else {{
        fallbackCopy(url, btn, originalText);
      }}
    }}

    function fallbackCopy(url, btn, originalText) {{
      const ta = document.createElement('textarea');
      ta.value = url;
      document.body.appendChild(ta);
      ta.select();
      try {{
        document.execCommand('copy');
        showToast('원문 기사 링크가 복사되었습니다.');
        btn.innerHTML = '✓ 복사 완료';
        btn.classList.add('copied');
        setTimeout(() => {{
          btn.innerHTML = originalText;
          btn.classList.remove('copied');
        }}, 2000);
      }} catch (e) {{
        alert('링크 복사에 실패했습니다.');
      }}
      document.body.removeChild(ta);
    }}

    function showToast(msg) {{
      const toast = document.getElementById('tossToast');
      if (!toast) return;
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => {{
        toast.classList.remove('show');
      }}, 2400);
    }}

    // Mobile Drawer Controls
    function toggleMobileMenu() {{
      const sidebar = document.querySelector('.context-sidebar');
      const backdrop = document.getElementById('drawerBackdrop');
      const menuBtn = document.getElementById('mobileMenuBtn');
      if (!sidebar) return;
      const isOpen = sidebar.classList.toggle('open');
      if (backdrop) backdrop.classList.toggle('open', isOpen);
      if (menuBtn) menuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    }}

    function closeMobileMenu() {{
      const sidebar = document.querySelector('.context-sidebar');
      const backdrop = document.getElementById('drawerBackdrop');
      const menuBtn = document.getElementById('mobileMenuBtn');
      if (sidebar) sidebar.classList.remove('open');
      if (backdrop) backdrop.classList.remove('open');
      if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
    }}

    // Keyboard accessibility
    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') {{
        closeMobileMenu();
        if (searchQuery.length > 0) clearSearch();
      }}
    }});

    // Theme Management with Persistence
    function initTheme() {{
      const saved = localStorage.getItem('daily_intel_theme');
      if (saved === 'dark' || saved === 'light') {{
        setTheme(saved);
      }} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {{
        setTheme('light');
      }} else {{
        setTheme('dark');
      }}
    }}

    function setTheme(theme) {{
      document.documentElement.setAttribute('data-theme', theme);
      try {{ localStorage.setItem('daily_intel_theme', theme); }} catch(e) {{}}
      const themeBtn = document.getElementById('themeBtn');
      if (themeBtn) {{
        themeBtn.textContent = theme === 'dark' ? '☀️ 라이트 모드' : '🌙 다크 모드';
      }}
    }}

    function toggleTheme() {{
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    }}

    // Run on load
    initTheme();
  </script>
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
