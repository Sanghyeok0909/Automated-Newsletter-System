import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup

# Ensure src is importable
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(repo_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from config import (
    ARTICLES_PER_PUBLISHER,
    CANDIDATES_PER_PUBLISHER,
    FRESHNESS_HOURS,
    PUBLISHERS,
    PUBLISHER_BY_NAME
)
from fetcher import (
    canonicalize_url,
    is_eligible_candidate,
    score_article
)
from generator import render_html_template

class TestCurationExpansion(unittest.TestCase):

    def test_central_configuration(self):
        """Verify centralized target of 5 articles per publisher and bounded candidate pool."""
        self.assertEqual(ARTICLES_PER_PUBLISHER, 5)
        self.assertEqual(CANDIDATES_PER_PUBLISHER, 20)
        self.assertEqual(FRESHNESS_HOURS, 24)
        self.assertEqual(len(PUBLISHERS), 5)
        expected_names = {"The Verge", "TechCrunch", "Ars Technica", "MIT Tech Review", "The Information"}
        self.assertEqual(set(PUBLISHER_BY_NAME.keys()), expected_names)

    def test_canonical_url_tracking_cleanup(self):
        """Verify tracking parameters are safely stripped while preserving paths and valid params."""
        raw_url = "https://www.theverge.com/news/12345/ai-announcement?utm_source=twitter&utm_medium=social&utm_campaign=launch&id=99"
        clean = canonicalize_url(raw_url)
        self.assertNotIn("utm_source", clean)
        self.assertNotIn("utm_medium", clean)
        self.assertNotIn("utm_campaign", clean)
        self.assertIn("id=99", clean)

        gnews_url = "https://news.google.com/rss/articles/CBMi12345?oc=5"
        clean_gnews = canonicalize_url(gnews_url)
        self.assertNotIn("oc=5", clean_gnews)
        self.assertIn("articles/CBMi12345", clean_gnews)

    def test_candidate_eligibility_filter(self):
        """Verify commercial, shopping, and trivial stub content are excluded."""
        # Shopping / promotional content
        self.assertFalse(is_eligible_candidate("The best Prime Day tech deals of 2026", "Save $50 on smart speakers"))
        self.assertFalse(is_eligible_candidate("Huge discount on OLED TVs: 40% off coupon", "Check our buyer's guide"))
        self.assertFalse(is_eligible_candidate("Best phone cases for iPhone 18", "Review: our top picks"))

        # Stub / login content
        self.assertFalse(is_eligible_candidate("Login", "MIT Technology Review login page"))
        self.assertFalse(is_eligible_candidate("Sign In", "Sign in to continue reading"))
        self.assertFalse(is_eligible_candidate("Hi", "Short"))

        # Legitimate substantive news
        self.assertTrue(is_eligible_candidate("DOJ files antitrust lawsuit against tech conglomerate", "Federal prosecutors claim anticompetitive monopoly practices"))
        self.assertTrue(is_eligible_candidate("OpenAI unveils next-generation multimodal model architecture", "The new foundation model achieves state-of-the-art benchmarks"))

    def test_importance_ranking_rubric(self):
        """Verify high-impact news outranks trivial items deterministically."""
        now = datetime.now(timezone.utc)
        recent_date = now - timedelta(hours=2)

        # High impact development
        high_impact = score_article(
            title="FTC opens antitrust investigation into major cloud provider's $10 billion AI chip cluster",
            summary="Federal regulators issued subpoenas regarding anticompetitive exclusive foundry contracts with TSMC and Nvidia.",
            pub_date=recent_date,
            now=now
        )

        # Trivial / minor development
        low_impact = score_article(
            title="A fresh new colorway is arriving for retro mechanical keycaps",
            summary="The boutique peripheral maker announced a pastel palette update for keyboards.",
            pub_date=recent_date,
            now=now
        )

        self.assertGreater(high_impact["total_score"], low_impact["total_score"])
        self.assertGreater(high_impact["impact"], 0)
        self.assertEqual(high_impact["recency"], 10)

        # Deterministic stability
        high_impact_repeat = score_article(
            title="FTC opens antitrust investigation into major cloud provider's $10 billion AI chip cluster",
            summary="Federal regulators issued subpoenas regarding anticompetitive exclusive foundry contracts with TSMC and Nvidia.",
            pub_date=recent_date,
            now=now
        )
        self.assertEqual(high_impact["total_score"], high_impact_repeat["total_score"])

    def test_generator_renders_full_25_articles(self):
        """Verify that a complete 25-article edition renders exactly 25 cards with matching counts."""
        articles_25 = []
        for p in PUBLISHERS:
            for i in range(5):
                articles_25.append({
                    "media": p["name"],
                    "title": f"{p['name']} Article {i+1} Title",
                    "korean_title": f"{p['name']} 기사 {i+1} 핵심 분석",
                    "link": f"https://example.com/{p['slug']}/{i+1}",
                    "published_at": "2026-09-18T10:00:00",
                    "summary_3_lines": [
                        f"{p['name']} 핵심 내용 1",
                        f"{p['name']} 핵심 내용 2",
                        f"{p['name']} 핵심 내용 3"
                    ],
                    "business_insight": f"{p['name']} 기사의 시장 및 기술 시사점입니다."
                })

        html = render_html_template(articles_25, "2026-09-18")
        soup = BeautifulSoup(html, "html.parser")

        cards = soup.find_all("article", class_="toss-card")
        self.assertEqual(len(cards), 25)

        # Verify hero count shows 25
        hero_count = soup.find("span", id="heroArticleCount")
        self.assertIn("25개", hero_count.text)

        # Verify right rail shows 25
        meta_count = soup.find("span", id="metaVisibleCount")
        self.assertIn("25개", meta_count.text)

        # Verify each publisher sidebar count shows 5
        for p in PUBLISHERS:
            badge = soup.find("span", id=f"channel-count-{p['slug']}")
            self.assertEqual(badge.text.strip(), "5")

        # Verify reading time is dynamic (for 25 articles, should be >= 10 minutes, definitely not hardcoded 3분)
        metric_cards = soup.find_all("div", class_="metric-card")
        reading_time_card = [m for m in metric_cards if "예상 리딩 소요시간" in m.text][0]
        self.assertNotIn("약 3분", reading_time_card.text)

    def test_generator_renders_partial_edition_honestly(self):
        """Verify that partial editions reflect their actual counts truthfully without placeholder fabrication."""
        articles_partial = [
            {
                "media": "The Verge",
                "title": "Verge 1",
                "korean_title": "더버지 기사 1",
                "link": "https://example.com/v1",
                "summary_3_lines": ["요약1", "요약2", "요약3"],
                "business_insight": "인사이트"
            },
            {
                "media": "The Verge",
                "title": "Verge 2",
                "korean_title": "더버지 기사 2",
                "link": "https://example.com/v2",
                "summary_3_lines": ["요약1", "요약2", "요약3"],
                "business_insight": "인사이트"
            },
            {
                "media": "The Verge",
                "title": "Verge 3",
                "korean_title": "더버지 기사 3",
                "link": "https://example.com/v3",
                "summary_3_lines": ["요약1", "요약2", "요약3"],
                "business_insight": "인사이트"
            }
        ]

        html = render_html_template(articles_partial, "2026-09-18")
        soup = BeautifulSoup(html, "html.parser")

        cards = soup.find_all("article", class_="toss-card")
        self.assertEqual(len(cards), 3)

        hero_count = soup.find("span", id="heroArticleCount")
        self.assertIn("3개", hero_count.text)

        meta_count = soup.find("span", id="metaVisibleCount")
        self.assertIn("3개", meta_count.text)

        # The Verge should show 3, others show 0
        self.assertEqual(soup.find("span", id="channel-count-verge").text.strip(), "3")
        self.assertEqual(soup.find("span", id="channel-count-techcrunch").text.strip(), "0")

    def test_historical_10_article_edition_compatibility(self):
        """Verify historical 10-article editions render correctly with actual counts."""
        articles_10 = []
        for p in PUBLISHERS:
            for i in range(2):
                articles_10.append({
                    "media": p["name"],
                    "title": f"{p['name']} Hist {i+1}",
                    "korean_title": f"{p['name']} 과거 기사 {i+1}",
                    "link": f"https://example.com/{p['slug']}/hist/{i+1}",
                    "summary_3_lines": ["과거 요약 1", "과거 요약 2", "과거 요약 3"],
                    "business_insight": "과거 인사이트"
                })

        html = render_html_template(articles_10, "2026-09-15")
        soup = BeautifulSoup(html, "html.parser")

        cards = soup.find_all("article", class_="toss-card")
        self.assertEqual(len(cards), 10)
        self.assertIn("10개", soup.find("span", id="heroArticleCount").text)
        self.assertIn("10개", soup.find("span", id="metaVisibleCount").text)

if __name__ == "__main__":
    unittest.main()
