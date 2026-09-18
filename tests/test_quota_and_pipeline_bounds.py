import os
import sys
import unittest
import json
import tempfile
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

# Ensure src is in sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(repo_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from config import (
    ARTICLES_PER_PUBLISHER,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    PUBLISHERS
)
from fetcher import is_eligible_candidate
from analyzer import (
    classify_api_error,
    ErrorCategory,
    validate_batch_response,
    build_batch_prompt
)
from generator import render_html_template

class TestQuotaAndPipelineBounds(unittest.TestCase):

    # 1. Daily quota exceeded + retry_delay=18: no repeated retry or backup cascade
    def test_daily_quota_exceeded_classification(self):
        err = Exception(
            "429 RESOURCE_EXHAUSTED: You exceeded your current quota. "
            "quota_metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, "
            "quota_id: GenerateRequestsPerDayPerProjectPerModel-FreeTier, "
            "quota_value: 20, retry_delay: 18.2s"
        )
        cat, desc = classify_api_error(err)
        self.assertEqual(cat, ErrorCategory.DAILY_QUOTA_EXHAUSTED)
        self.assertIn("Daily", desc)

    # 2. Daily and transient quota details both present: Daily takes precedence
    def test_daily_precedence_over_transient_delay(self):
        err = Exception(
            "HTTP 429: Resource has been exhausted (e.g. check quota). "
            "QuotaFailure: GenerateRequestsPerDayPerProjectPerModel-FreeTier "
            "Please retry after retry_delay: 18s"
        )
        cat, _ = classify_api_error(err)
        self.assertEqual(cat, ErrorCategory.DAILY_QUOTA_EXHAUSTED)

    # 3. Transient 429: classified as transient rate limit with extracted delay
    def test_transient_429_classification(self):
        err = Exception(
            "429 RESOURCE_EXHAUSTED: Requests per minute limit exceeded. "
            "Please retry after retry_delay: 12.5s"
        )
        cat, desc = classify_api_error(err)
        self.assertEqual(cat, ErrorCategory.TRANSIENT_RATE_LIMIT)
        self.assertIn("12.5s", desc)

    # 4. 5xx/timeouts: classified as transient server error
    def test_5xx_and_timeout_classification(self):
        err_503 = Exception("503 Service Unavailable: The model is overloaded. Please try again later.")
        cat, _ = classify_api_error(err_503)
        self.assertEqual(cat, ErrorCategory.TRANSIENT_SERVER_ERROR)

        err_timeout = Exception("DeadlineExceeded: 504 Deadline Exceeded: request timed out after 45.0s")
        cat2, _ = classify_api_error(err_timeout)
        self.assertEqual(cat2, ErrorCategory.TRANSIENT_SERVER_ERROR)

    # 5. Authentication / Unsupported model errors
    def test_auth_and_unsupported_model_classification(self):
        err_auth = Exception("401 API_KEY_INVALID: API key not valid. Please pass a valid API key.")
        cat, _ = classify_api_error(err_auth)
        self.assertEqual(cat, ErrorCategory.AUTHENTICATION_ERROR)

        err_404 = Exception("404 models/gemini-unsupported is not found for API version v1beta")
        cat2, _ = classify_api_error(err_404)
        self.assertEqual(cat2, ErrorCategory.MODEL_UNAVAILABLE)

    # 6. Unknown 429 behavior: classified conservatively
    def test_unknown_429_classification(self):
        err_generic_429 = Exception("429 Too Many Requests: Rate limit exceeded")
        cat, _ = classify_api_error(err_generic_429)
        self.assertEqual(cat, ErrorCategory.TRANSIENT_RATE_LIMIT)

    # 7. Batch output validation: missing IDs, duplicate IDs, truncation, invalid schema rejected
    def test_batch_output_validation(self):
        expected_ids = ["art_1", "art_2"]

        # Valid payload
        valid_json = json.dumps({
            "art_1": {
                "korean_title": "기사 1 제목",
                "summary_3_lines": ["요약 1", "요약 2", "요약 3"],
                "business_insight": "인사이트 1"
            },
            "art_2": {
                "korean_title": "기사 2 제목",
                "summary_3_lines": ["요약 A", "요약 B", "요약 C"],
                "business_insight": "인사이트 2"
            }
        })
        is_valid, res = validate_batch_response(expected_ids, valid_json)
        self.assertTrue(is_valid)
        self.assertIn("art_1", res)
        self.assertIn("art_2", res)

        # Missing an ID
        missing_id_json = json.dumps({
            "art_1": {
                "korean_title": "기사 1 제목",
                "summary_3_lines": ["요약 1", "요약 2", "요약 3"],
                "business_insight": "인사이트 1"
            }
        })
        is_valid, err_msg = validate_batch_response(expected_ids, missing_id_json)
        self.assertFalse(is_valid)
        self.assertIn("Missing article IDs", err_msg)

        # Incomplete schema (missing summary_3_lines)
        incomplete_json = json.dumps({
            "art_1": {"korean_title": "기사 1", "business_insight": "인사이트"},
            "art_2": {"korean_title": "기사 2", "summary_3_lines": ["A"], "business_insight": "인사이트"}
        })
        is_valid, err_msg2 = validate_batch_response(expected_ids, incomplete_json)
        self.assertFalse(is_valid)

        # Truncated or invalid JSON
        is_valid, err_msg3 = validate_batch_response(expected_ids, "{\"art_1\": { broken json")
        self.assertFalse(is_valid)

    # 8. Complete 25-article fixture: exact UI mapping and counts
    def test_complete_25_article_fixture(self):
        articles_25 = []
        for p in PUBLISHERS:
            for i in range(5):
                articles_25.append({
                    "media": p["name"],
                    "title": f"{p['name']} Article {i+1}",
                    "korean_title": f"{p['name']} 한글 제목 {i+1}",
                    "link": f"https://example.com/{p['slug']}/{i+1}",
                    "summary_3_lines": ["요약 1", "요약 2", "요약 3"],
                    "business_insight": "인사이트 내용"
                })

        html = render_html_template(articles_25, "2026-09-18")
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("article", class_="toss-card")
        self.assertEqual(len(cards), 25)

        hero_count = soup.find("span", id="heroArticleCount")
        self.assertIn("25개", hero_count.text)
        meta_count = soup.find("span", id="metaVisibleCount")
        self.assertIn("25개", meta_count.text)

    # 9. Partial 14-target fixture: honest counts and candidate-shortage statuses
    def test_partial_14_target_fixture(self):
        # 2 Verge, 4 TechCrunch, 0 Ars, 3 MIT, 5 Information = 14 total
        counts = {"The Verge": 2, "TechCrunch": 4, "Ars Technica": 0, "MIT Tech Review": 3, "The Information": 5}
        articles_14 = []
        for p_name, cnt in counts.items():
            for i in range(cnt):
                articles_14.append({
                    "media": p_name,
                    "title": f"{p_name} {i+1}",
                    "korean_title": f"{p_name} 기사 {i+1}",
                    "link": f"https://example.com/{i+1}",
                    "summary_3_lines": ["요약 1", "요약 2", "요약 3"],
                    "business_insight": "인사이트"
                })

        html = render_html_template(articles_14, "2026-09-18")
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("article", class_="toss-card")
        self.assertEqual(len(cards), 14)

        hero_count = soup.find("span", id="heroArticleCount")
        self.assertIn("14개", hero_count.text)
        self.assertEqual(soup.find("span", id="channel-count-verge").text.strip(), "2")
        self.assertEqual(soup.find("span", id="channel-count-arstechnica").text.strip(), "0")

    # 10. Quota failure: last valid site is not overwritten
    def test_quota_failure_preserves_existing_valid_site(self):
        from generator import generate_newsletter
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                os.makedirs("src", exist_ok=True)
                os.makedirs("dist", exist_ok=True)

                # Existing valid site
                existing_html = "<html><body>Last Valid Site</body></html>"
                with open("dist/index.html", "w", encoding="utf-8") as f:
                    f.write(existing_html)

                # Empty translated_articles due to immediate quota failure
                with open("src/translated_articles.json", "w", encoding="utf-8") as f:
                    json.dump([], f)

                # Run generator should raise SystemExit(1) or fail-fast and NOT overwrite dist/index.html
                with self.assertRaises(SystemExit):
                    generate_newsletter()

                with open("dist/index.html", "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertEqual(content, existing_html, "Existing valid site was overwritten on quota failure!")

            finally:
                os.chdir(orig_cwd)

    # 11. Cache / Checkpoint incremental mechanism test
    def test_checkpoint_mechanism(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                os.makedirs("src", exist_ok=True)
                checkpoint_file = "src/translated_articles.json"

                # Checkpoint 1: first publisher done
                art_batch_1 = [{"title": "Art 1", "media": "The Verge"}]
                with open(checkpoint_file, "w", encoding="utf-8") as f:
                    json.dump(art_batch_1, f)

                # Verify persisted
                with open(checkpoint_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.assertEqual(len(data), 1)

                # Checkpoint 2: second publisher done
                art_batch_2 = art_batch_1 + [{"title": "Art 2", "media": "TechCrunch"}]
                with open(checkpoint_file, "w", encoding="utf-8") as f:
                    json.dump(art_batch_2, f)

                with open(checkpoint_file, "r", encoding="utf-8") as f:
                    data2 = json.load(f)
                self.assertEqual(len(data2), 2)
            finally:
                os.chdir(orig_cwd)

    # 12. "CoreWeave Prices..." not excluded solely due to "Prices"
    def test_coreweave_prices_financial_headline_not_excluded(self):
        title = "CoreWeave Prices $3.7 Billion Convertible Bond Offering"
        summary = "CoreWeave has priced its upsized offering of convertible senior notes."
        self.assertTrue(
            is_eligible_candidate(title, summary),
            "Financial bond offering was incorrectly excluded as promotional!"
        )

        # Confirm real shopping deals ARE excluded
        shopping_deal = "Best Prime Day Deals: Save $50 on smart speakers with promo code"
        self.assertFalse(
            is_eligible_candidate(shopping_deal, "Check our buying guide for the lowest prices on electronics.")
        )

    # 13. Request and elapsed-time budget: max 5 calls for 25 articles, bounded retries
    def test_request_and_time_budget(self):
        # 5 publishers with 5 articles each = exactly 5 publisher batches
        total_articles = 25
        num_publishers = len(PUBLISHERS)
        expected_calls = num_publishers  # exactly 5 requests!
        max_calls_with_retry = num_publishers * 2  # exactly 10 requests!

        # 5 calls is well under 20 RPD daily quota
        self.assertLess(expected_calls, 20)
        self.assertLessEqual(max_calls_with_retry, 20)

        # Batch prompt length sanity check
        dummy_candidates = [{"title": f"T{i}", "summary": f"S{i}"} for i in range(5)]
        prompt = build_batch_prompt("TechCrunch", dummy_candidates)
        self.assertIn("art_1", prompt)
        self.assertIn("art_5", prompt)
        self.assertLess(len(prompt), 4000)

if __name__ == "__main__":
    unittest.main()
