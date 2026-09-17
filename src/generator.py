import json
import os
import sys
from datetime import datetime
from html import escape as html_escape

def render_html_template(articles, today_str):
    """
    디스코드(Discord)의 4단계 매크로 아키텍처(글로벌 레일, 채널 사이드바, 메인 워크스페이스, 메타 패널)와
    토스(Toss)의 마이크로 인터랙션(고대비 타이포그래피, 20px+ 소프트 곡률, 스프링 햅틱 피드백)을
    완벽히 융합한 자가완결형(Self-Contained) 반응형 웹사이트 템플릿
    """
    # 매체별 고유 식별자(slug) 매핑 및 통계 산출
    media_slug_map = {
        "The Verge": "verge",
        "TechCrunch": "techcrunch",
        "Ars Technica": "arstechnica",
        "MIT Tech Review": "mit",
        "The Information": "theinformation"
    }

    media_counts = {}
    for art in articles:
        m = art.get("media", "Tech Media")
        media_counts[m] = media_counts.get(m, 0) + 1

    # 기사 카드 HTML 생성
    article_cards = []
    for idx, article in enumerate(articles):
        k_title = article.get("korean_title", article.get("title", "제목 없음"))
        k_summary = article.get("summary_3_lines", [])
        insight = article.get("business_insight", "인사이트를 추출할 수 없습니다.")
        link = article.get("link", "#")
        media = article.get("media", "Tech Media")
        slug = media_slug_map.get(media, "general")

        summary_items = ""
        if isinstance(k_summary, list):
            for item in k_summary:
                summary_items += f'              <li class="summary-bullet">{html_escape(str(item))}</li>\n'
        elif isinstance(k_summary, str):
            summary_items += f'              <li class="summary-bullet">{html_escape(k_summary)}</li>\n'

        card_html = f"""        <!-- Toss-Style Tactile Article Card -->
        <article class="toss-card" data-media="{slug}" id="article-{idx+1}">
          <div class="card-top-rail">
            <div class="media-identity">
              <span class="media-avatar {slug}"></span>
              <div class="media-meta">
                <span class="media-name">{html_escape(media)}</span>
                <span class="channel-slug">#{slug}-feed</span>
              </div>
            </div>
            <a href="{link}" target="_blank" rel="noopener noreferrer" class="toss-pill-link" aria-label="원문 보기">
              원문 읽기 ↗
            </a>
          </div>

          <h2 class="card-headline">{html_escape(k_title)}</h2>

          <div class="toss-surface-box">
            <div class="section-badge">핵심 3줄 요약</div>
            <ul class="summary-bullet-list">
{summary_items}            </ul>
          </div>

          <div class="toss-insight-card">
            <div class="insight-pill">
              <span class="insight-icon">💡</span>
              <span class="insight-tag">비즈니스 인사이트</span>
            </div>
            <p class="insight-description">{html_escape(insight)}</p>
          </div>

          <div class="card-footer-action">
            <button class="toss-secondary-btn" onclick="navigator.clipboard.writeText('{link}'); alert('원문 기사 링크가 복사되었습니다.');">
              🔗 링크 복사
            </button>
            <span class="reading-time">소요시간 약 45초</span>
          </div>
        </article>"""
        article_cards.append(card_html)

    cards_html_content = "\n\n".join(article_cards)

    full_html = f"""<!DOCTYPE html>
<html lang="ko" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <meta name="description" content="Daily Tech Insights: {today_str} - 디스코드 레이아웃과 토스 디자인 시스템이 융합된 실시간 글로벌 테크 인텔리전스">
  <title>Daily Tech Insights | {today_str}</title>
  <style>
    /* ==========================================================================
       Discord Macro-Layout & Toss Micro-Interaction Hybrid Design System
       Pure Vanilla CSS3 / Zero Dependencies / Self-Contained
       ========================================================================== */
    
    :root {{
      /* Toss Pure & High Contrast Palette */
      --toss-blue: #3182f6;
      --toss-blue-hover: #1b64da;
      --toss-blue-subtle: rgba(49, 130, 246, 0.12);
      --toss-blue-glow: rgba(49, 130, 246, 0.25);
      
      /* Discord Macro Structural Colors (Dark Theme) */
      --rail-bg: #1e1f22;
      --sidebar-bg: #2b2d31;
      --chat-bg: #313338;
      --surface-card: #2b2d31;
      --surface-inset: #1e1f22;
      --surface-hover: #35373c;
      --surface-active: #3f4248;
      
      --text-header: #f2f3f5;
      --text-normal: #dbdee1;
      --text-muted: #949ba4;
      --text-link: #00a8fc;
      
      --border-subtle: rgba(255, 255, 255, 0.07);
      --border-strong: rgba(255, 255, 255, 0.12);
      
      --font-toss: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      --spring-physics: all 0.24s cubic-bezier(0.34, 1.56, 0.64, 1);
      --spring-tap: transform 0.12s cubic-bezier(0.4, 0, 0.2, 1);
      
      --radius-toss: 22px;
      --radius-sm: 12px;
    }}

    [data-theme="light"] {{
      --rail-bg: #e3e5e8;
      --sidebar-bg: #f2f3f5;
      --chat-bg: #ffffff;
      --surface-card: #f8f9fa;
      --surface-inset: #ffffff;
      --surface-hover: #e9ecef;
      --surface-active: #dee2e6;
      
      --text-header: #191f28;
      --text-normal: #333d4b;
      --text-muted: #8b95a1;
      --text-link: #3182f6;
      
      --border-subtle: rgba(0, 0, 0, 0.06);
      --border-strong: rgba(0, 0, 0, 0.12);
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
      font-family: var(--font-toss);
      background-color: var(--chat-bg);
      color: var(--text-normal);
      line-height: 1.6;
      word-break: keep-all;
      -webkit-font-smoothing: antialiased;
    }}

    /* App Shell Grid (Level 0) */
    .discord-app-shell {{
      display: flex;
      width: 100%;
      height: 100%;
    }}

    /* ==========================================================================
       Level 1: Global Rail (Discord Server Rail)
       ========================================================================== */
    .global-rail {{
      width: 72px;
      min-width: 72px;
      height: 100%;
      background-color: var(--rail-bg);
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 12px 0;
      gap: 8px;
      z-index: 30;
      border-right: 1px solid var(--border-subtle);
    }}

    .rail-btn {{
      position: relative;
      width: 48px;
      height: 48px;
      border-radius: 24px;
      background-color: var(--sidebar-bg);
      color: var(--text-normal);
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      font-weight: 800;
      transition: var(--spring-physics);
    }}

    .rail-btn:hover {{
      border-radius: 16px;
      background-color: var(--toss-blue);
      color: #ffffff;
      transform: scale(1.05);
      box-shadow: 0 4px 14px var(--toss-blue-glow);
    }}

    .rail-btn:active {{
      transform: scale(0.92);
    }}

    .rail-btn.active {{
      border-radius: 16px;
      background-color: var(--toss-blue);
      color: #ffffff;
    }}

    .rail-btn.active::before {{
      content: "";
      position: absolute;
      left: -12px;
      width: 4px;
      height: 36px;
      border-radius: 0 4px 4px 0;
      background-color: #ffffff;
    }}

    .rail-divider {{
      width: 32px;
      height: 2px;
      background-color: var(--border-subtle);
      margin: 4px 0;
      border-radius: 1px;
    }}

    /* ==========================================================================
       Level 2: Context Sidebar (Discord Channels + Toss Control)
       ========================================================================== */
    .context-sidebar {{
      width: 240px;
      min-width: 240px;
      height: 100%;
      background-color: var(--sidebar-bg);
      display: flex;
      flex-direction: column;
      border-right: 1px solid var(--border-subtle);
      z-index: 20;
    }}

    .server-header {{
      height: 48px;
      padding: 0 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-subtle);
      font-weight: 800;
      font-size: 0.95rem;
      color: var(--text-header);
      box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }}

    .server-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .channels-scroll {{
      flex: 1;
      overflow-y: auto;
      padding: 12px 8px;
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
      padding: 12px 8px 4px 8px;
    }}

    .channel-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 10px;
      border-radius: 8px;
      color: var(--text-muted);
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
      transition: var(--spring-physics);
      text-decoration: none;
    }}

    .channel-item:hover {{
      background-color: var(--surface-hover);
      color: var(--text-header);
      transform: translateX(3px);
    }}

    .channel-item.active {{
      background-color: var(--surface-active);
      color: var(--text-header);
      font-weight: 700;
    }}

    .channel-left {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .channel-hash {{
      font-size: 1.05rem;
      opacity: 0.7;
    }}

    .channel-count {{
      font-size: 0.72rem;
      background-color: var(--surface-inset);
      padding: 2px 6px;
      border-radius: 10px;
      font-weight: 700;
    }}

    /* Sidebar User Profile Tray */
    .sidebar-user-tray {{
      height: 56px;
      background-color: var(--rail-bg);
      padding: 0 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .user-info-box {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .status-dot {{
      width: 10px;
      height: 10px;
      background-color: #23a55a;
      border-radius: 50%;
      box-shadow: 0 0 8px #23a55a;
    }}

    .user-name-label {{
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-header);
      line-height: 1.2;
    }}

    .user-sub-label {{
      font-size: 0.7rem;
      color: var(--text-muted);
    }}

    /* ==========================================================================
       Level 3: Primary Workspace (Toss Micro-Interaction Canvas)
       ========================================================================== */
    .chat-workspace {{
      flex: 1;
      height: 100%;
      display: flex;
      flex-direction: column;
      background-color: var(--chat-bg);
      overflow: hidden;
      position: relative;
    }}

    /* Top Workspace Header */
    .workspace-header {{
      height: 48px;
      padding: 0 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-subtle);
      background-color: var(--chat-bg);
      z-index: 10;
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
      height: 16px;
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
      border-radius: 12px;
      background-color: var(--surface-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-normal);
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      transition: var(--spring-physics);
    }}

    .theme-toggle-btn:hover {{
      background-color: var(--surface-hover);
      transform: translateY(-1px);
    }}

    .theme-toggle-btn:active {{
      transform: scale(0.94);
    }}

    /* Scrollable Feed Area */
    .messages-feed {{
      flex: 1;
      overflow-y: auto;
      padding: 24px 28px 60px 28px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 24px;
    }}

    /* Welcome Hero Banner (Discord Channel Start Aesthetic) */
    .feed-hero {{
      width: 100%;
      max-width: 720px;
      background: linear-gradient(135deg, var(--surface-card) 0%, var(--surface-inset) 100%);
      border: 1px solid var(--border-strong);
      border-radius: var(--radius-toss);
      padding: 28px 24px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      margin-bottom: 6px;
    }}

    .hero-badge-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
    }}

    .toss-tag {{
      font-size: 0.75rem;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 9999px;
      background-color: var(--toss-blue-subtle);
      color: var(--toss-blue);
      letter-spacing: 0.02em;
    }}

    .hero-title {{
      font-size: 1.85rem;
      font-weight: 900;
      letter-spacing: -0.03em;
      color: var(--text-header);
      margin-bottom: 8px;
      line-height: 1.25;
    }}

    .hero-subtitle {{
      font-size: 0.95rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    /* ==========================================================================
       Toss Micro-Architecture: Article Cards
       ========================================================================== */
    .toss-card {{
      width: 100%;
      max-width: 720px;
      background-color: var(--surface-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-toss);
      padding: 24px 22px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
      transition: var(--spring-physics);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .toss-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
      border-color: var(--toss-blue-glow);
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
      width: 36px;
      height: 36px;
      border-radius: 12px;
      background-color: var(--toss-blue);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      color: #ffffff;
      font-size: 0.85rem;
      box-shadow: 0 2px 6px var(--toss-blue-glow);
    }}
    .media-avatar.verge {{ background: linear-gradient(135deg, #e0005a, #fa2d60); }}
    .media-avatar.techcrunch {{ background: linear-gradient(135deg, #029924, #00d235); }}
    .media-avatar.arstechnica {{ background: linear-gradient(135deg, #ff4e00, #ff8100); }}
    .media-avatar.mit {{ background: linear-gradient(135deg, #000000, #555555); }}
    .media-avatar.theinformation {{ background: linear-gradient(135deg, #0d253f, #1b497a); }}

    .media-name {{
      font-size: 0.92rem;
      font-weight: 800;
      color: var(--text-header);
    }}

    .channel-slug {{
      display: block;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
    }}

    .toss-pill-link {{
      font-size: 0.82rem;
      font-weight: 800;
      padding: 6px 14px;
      border-radius: 9999px;
      background-color: var(--toss-blue-subtle);
      color: var(--toss-blue);
      text-decoration: none;
      transition: var(--spring-physics);
    }}

    .toss-pill-link:hover {{
      background-color: var(--toss-blue);
      color: #ffffff;
      transform: scale(1.05);
    }}

    .toss-pill-link:active {{
      transform: scale(0.94);
    }}

    .card-headline {{
      font-size: 1.35rem;
      font-weight: 800;
      letter-spacing: -0.025em;
      color: var(--text-header);
      line-height: 1.38;
    }}

    /* Toss Inset Box */
    .toss-surface-box {{
      background-color: var(--surface-inset);
      border-radius: var(--radius-sm);
      padding: 16px 18px;
      border: 1px solid var(--border-subtle);
    }}

    .section-badge {{
      font-size: 0.75rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 8px;
    }}

    .summary-bullet-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .summary-bullet {{
      position: relative;
      padding-left: 18px;
      font-size: 0.95rem;
      color: var(--text-normal);
      line-height: 1.6;
    }}

    .summary-bullet::before {{
      content: "•";
      position: absolute;
      left: 2px;
      color: var(--toss-blue);
      font-weight: 900;
      font-size: 1.2rem;
      line-height: 1;
    }}

    /* Toss Insight Callout */
    .toss-insight-card {{
      background-color: var(--toss-blue-subtle);
      border-left: 4px solid var(--toss-blue);
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      padding: 14px 18px;
    }}

    .insight-pill {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      font-weight: 800;
      color: var(--toss-blue);
      margin-bottom: 6px;
    }}

    .insight-description {{
      font-size: 0.93rem;
      font-weight: 600;
      color: var(--text-header);
      line-height: 1.6;
    }}

    .card-footer-action {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 4px;
    }}

    .toss-secondary-btn {{
      border: none;
      background-color: var(--surface-inset);
      color: var(--text-muted);
      font-size: 0.82rem;
      font-weight: 700;
      padding: 6px 14px;
      border-radius: 10px;
      cursor: pointer;
      transition: var(--spring-physics);
    }}

    .toss-secondary-btn:hover {{
      background-color: var(--surface-hover);
      color: var(--text-header);
    }}

    .toss-secondary-btn:active {{
      transform: scale(0.94);
    }}

    .reading-time {{
      font-size: 0.78rem;
      color: var(--text-muted);
      font-weight: 600;
    }}

    /* ==========================================================================
       Level 4: Metadata Panel (Right Context Rail)
       ========================================================================== */
    .metadata-panel {{
      width: 250px;
      min-width: 250px;
      height: 100%;
      background-color: var(--sidebar-bg);
      border-left: 1px solid var(--border-subtle);
      padding: 16px 14px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      overflow-y: auto;
    }}

    .meta-group-title {{
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 8px;
    }}

    .metric-card {{
      background-color: var(--surface-card);
      border-radius: var(--radius-sm);
      padding: 12px 14px;
      border: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .metric-label {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 600;
    }}

    .metric-value {{
      font-size: 1.25rem;
      font-weight: 900;
      color: var(--toss-blue);
      letter-spacing: -0.02em;
    }}

    .feed-status-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 10px;
      border-radius: 8px;
      background-color: var(--surface-card);
      font-size: 0.8rem;
      font-weight: 700;
    }}

    .status-badge-active {{
      color: #23a55a;
      font-size: 0.75rem;
    }}

    /* ==========================================================================
       Mobile-First Responsive Adaptations
       ========================================================================== */
    @media (max-width: 1024px) {{
      .metadata-panel {{
        display: none;
      }}
    }}

    @media (max-width: 768px) {{
      .global-rail {{
        display: none;
      }}
      .context-sidebar {{
        display: none;
      }}
      .messages-feed {{
        padding: 16px 14px 40px 14px;
        gap: 16px;
      }}
      .feed-hero {{
        padding: 20px 16px;
      }}
      .hero-title {{
        font-size: 1.5rem;
      }}
      .toss-card {{
        padding: 20px 16px;
        border-radius: 18px;
      }}
      .card-headline {{
        font-size: 1.15rem;
      }}
      .topic-desc {{
        display: none;
      }}
    }}
  </style>
</head>
<body>
  <div class="discord-app-shell">
    
    <!-- Level 1: Global Rail (Discord Server Rail) -->
    <nav class="global-rail" aria-label="글로벌 서버 레일">
      <button class="rail-btn active" title="전체 브리핑 피드" onclick="filterFeed('all', this)">⚡</button>
      <div class="rail-divider"></div>
      <button class="rail-btn" title="The Verge" onclick="filterFeed('verge', this)">📱</button>
      <button class="rail-btn" title="TechCrunch" onclick="filterFeed('techcrunch', this)">🦄</button>
      <button class="rail-btn" title="Ars Technica" onclick="filterFeed('arstechnica', this)">⚙️</button>
      <button class="rail-btn" title="MIT Tech Review" onclick="filterFeed('mit', this)">🔬</button>
      <button class="rail-btn" title="The Information" onclick="filterFeed('theinformation', this)">📰</button>
    </nav>

    <!-- Level 2: Context Sidebar (Channels) -->
    <aside class="context-sidebar" aria-label="채널 네비게이션">
      <div class="server-header">
        <span class="server-badge">⚡ Tech Intel HQ</span>
        <span style="font-size: 0.8rem; color: var(--toss-blue);">✔</span>
      </div>

      <div class="channels-scroll">
        <div class="channel-category">데일리 피드</div>
        <a class="channel-item active" onclick="filterFeed('all', this)">
          <div class="channel-left">
            <span class="channel-hash">#</span>
            <span>📢-오늘의-브리핑</span>
          </div>
          <span class="channel-count">{len(articles)}</span>
        </a>

        <div class="channel-category">타겟 매체 채널</div>
        <a class="channel-item" onclick="filterFeed('verge', this)">
          <div class="channel-left">
            <span class="channel-hash">#</span>
            <span>📱-the-verge</span>
          </div>
          <span class="channel-count">{media_counts.get('The Verge', 0)}</span>
        </a>
        <a class="channel-item" onclick="filterFeed('techcrunch', this)">
          <div class="channel-left">
            <span class="channel-hash">#</span>
            <span>🦄-techcrunch</span>
          </div>
          <span class="channel-count">{media_counts.get('TechCrunch', 0)}</span>
        </a>
        <a class="channel-item" onclick="filterFeed('arstechnica', this)">
          <div class="channel-left">
            <span class="channel-hash">#</span>
            <span>⚙️-ars-technica</span>
          </div>
          <span class="channel-count">{media_counts.get('Ars Technica', 0)}</span>
        </a>
        <a class="channel-item" onclick="filterFeed('mit', this)">
          <div class="channel-left">
            <span class="channel-hash">#</span>
            <span>🔬-mit-tech-review</span>
          </div>
          <span class="channel-count">{media_counts.get('MIT Tech Review', 0)}</span>
        </a>
        <a class="channel-item" onclick="filterFeed('theinformation', this)">
          <div class="channel-left">
            <span class="channel-hash">#</span>
            <span>📰-the-information</span>
          </div>
          <span class="channel-count">{media_counts.get('The Information', 0)}</span>
        </a>
      </div>

      <div class="sidebar-user-tray">
        <div class="user-info-box">
          <div class="status-dot"></div>
          <div>
            <div class="user-name-label">Zero-Capital Agent</div>
            <div class="user-sub-label">GitHub Actions 파이프라인</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Level 3: Primary Workspace (Chat & Toss Cards) -->
    <main class="chat-workspace">
      <header class="workspace-header">
        <div class="topic-pill">
          <span># 📢-오늘의-브리핑</span>
          <div class="topic-divider"></div>
          <span class="topic-desc">글로벌 5대 테크 미디어 핵심 큐레이션 &amp; 비즈니스 인사이트</span>
        </div>
        <div class="header-controls">
          <button class="theme-toggle-btn" onclick="toggleTheme()" id="themeBtn">🌓 테마 전환</button>
        </div>
      </header>

      <section class="messages-feed" id="feedContainer">
        <!-- Hero Banner -->
        <div class="feed-hero">
          <div class="hero-badge-row">
            <span class="toss-tag">DAILY INTEL</span>
            <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 700;">{today_str}</span>
          </div>
          <h1 class="hero-title">Daily Tech Insights</h1>
          <p class="hero-subtitle">
            디스코드의 구조적 탐색 경험과 토스의 유려한 카드 인터랙션으로 글로벌 최신 기술 흐름을 빠르게 파악하십시오.
          </p>
        </div>

{cards_html_content}
      </section>
    </main>

    <!-- Level 4: Metadata Panel (Desktop Right Rail) -->
    <aside class="metadata-panel" aria-label="메타데이터 패널">
      <div class="meta-group-title">시스템 지표</div>
      <div class="metric-card">
        <span class="metric-label">총 큐레이션 기사</span>
        <span class="metric-value">{len(articles)}개</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">인프라 운영 비용</span>
        <span class="metric-value">$0.00</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">예상 리딩 소요시간</span>
        <span class="metric-value">약 3분</span>
      </div>

      <div class="meta-group-title">수집 소스 상태</div>
      <div class="feed-status-item">
        <span>The Verge</span>
        <span class="status-badge-active">정상 🟢</span>
      </div>
      <div class="feed-status-item">
        <span>TechCrunch</span>
        <span class="status-badge-active">정상 🟢</span>
      </div>
      <div class="feed-status-item">
        <span>Ars Technica</span>
        <span class="status-badge-active">정상 🟢</span>
      </div>
      <div class="feed-status-item">
        <span>MIT Tech Review</span>
        <span class="status-badge-active">정상 🟢</span>
      </div>
      <div class="feed-status-item">
        <span>The Information</span>
        <span class="status-badge-active">정상 🟢</span>
      </div>
    </aside>

  </div>

  <script>
    // 채널 및 레일 피드 필터링 인터랙션
    function filterFeed(slug, element) {{
      const cards = document.querySelectorAll('.toss-card');
      cards.forEach(card => {{
        if (slug === 'all' || card.getAttribute('data-media') === slug) {{
          card.style.display = 'flex';
        }} else {{
          card.style.display = 'none';
        }}
      }});

      // 액티브 상태 갱신
      document.querySelectorAll('.rail-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.channel-item').forEach(item => item.classList.remove('active'));
      if (element) {{
        element.classList.add('active');
      }}
    }}

    // 다크/라이트 테마 토글
    function toggleTheme() {{
      const html = document.documentElement;
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
    }}
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
