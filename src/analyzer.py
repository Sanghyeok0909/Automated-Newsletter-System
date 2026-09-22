import json
import time
import os
import sys
import re
from datetime import datetime, timezone
from collections import defaultdict
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure unbuffered real-time stdout in CI
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import (
    ARTICLES_PER_PUBLISHER,
    PUBLISHERS,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    VERIFIED_MODELS,
    API_TIMEOUT_SECONDS,
    MAX_BATCH_RETRIES,
    RATE_LIMIT_DELAY_SECONDS
)

def log(msg):
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now_str}] {msg}", flush=True)

class ErrorCategory:
    DAILY_QUOTA_EXHAUSTED = "DAILY_QUOTA_EXHAUSTED"
    TRANSIENT_RATE_LIMIT = "TRANSIENT_RATE_LIMIT"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    TRANSIENT_SERVER_ERROR = "TRANSIENT_SERVER_ERROR"
    SCHEMA_VALIDATION_ERROR = "SCHEMA_VALIDATION_ERROR"
    UNKNOWN = "UNKNOWN"

def classify_api_error(err):
    """
    Classifies Gemini API errors with structured priority:
    1. Daily quota exhaustion (PerDay / FreeTier limit)
    2. Authentication / Permission errors
    3. Model unavailable / 404
    4. Transient rate limits (RPM/TPM)
    5. Transient 5xx or timeouts
    6. Unknown errors
    """
    msg = str(err).lower()

    # 1. Daily Quota Exhaustion Detection
    # Matches quota_id 'GenerateRequestsPerDayPerProjectPerModel-FreeTier', 'perday', 'generaterequestsperday'
    if (
        "generaterequestsperday" in msg
        or "perday" in msg
        or ("exceeded your current quota" in msg and ("free_tier" in msg or "per project" in msg or "limit: 20" in msg or "limit: 15" in msg))
        or "free_tier_requests" in msg
    ):
        return ErrorCategory.DAILY_QUOTA_EXHAUSTED, "Daily per-project/per-model request quota exhausted."

    # 2. Authentication & Permission Errors
    if "401" in msg or "unauthenticated" in msg or "api key not valid" in msg or "invalid api key" in msg:
        return ErrorCategory.AUTHENTICATION_ERROR, "Invalid or missing GEMINI_API_KEY."
    if "403" in msg and "permission" in msg:
        return ErrorCategory.AUTHENTICATION_ERROR, "Permission denied for this API resource."

    # 3. Model Unavailable / 404
    if "404" in msg or "not found" in msg or "is not found for api version" in msg:
        return ErrorCategory.MODEL_UNAVAILABLE, "Configured model not found or unsupported."

    # 4. Transient Rate Limit (RPM/TPM)
    if "429" in msg or "resource_exhausted" in msg:
        retry_delay = 15.0
        m = re.search(r'retry_delay[:\s]+([\d\.]+)', msg)
        if m:
            try:
                retry_delay = float(m.group(1))
            except ValueError:
                pass
        return ErrorCategory.TRANSIENT_RATE_LIMIT, f"Transient rate limit (backoff: {retry_delay:.1f}s)"

    # 5. Transient Server Error (5xx) or Timeout
    if "503" in msg or "500" in msg or "deadline_exceeded" in msg or "timed out" in msg or "timeout" in msg:
        return ErrorCategory.TRANSIENT_SERVER_ERROR, "Server 5xx or connection timeout."

    return ErrorCategory.UNKNOWN, f"Unclassified API error: {str(err)[:120]}"

def build_batch_prompt(publisher_name, batch_candidates):
    """
    Builds a high-density, multi-article structured analysis prompt with stable IDs.
    """
    articles_payload = []
    for idx, c in enumerate(batch_candidates):
        art_id = f"art_{idx+1}"
        articles_payload.append(
            f"--- Article ID: {art_id} ---\n"
            f"Title: {c.get('title')}\n"
            f"Summary: {c.get('summary')}\n"
        )
    joined_articles = "\n".join(articles_payload)

    prompt = f"""
You are an elite tech analyst and editor for a premium daily briefing newsletter.
Read the following {len(batch_candidates)} articles from '{publisher_name}' and provide an objective, high-density structured JSON response in natural Korean.
Do not use markdown blocks (like ```json) in the output, just return the raw JSON object.

{joined_articles}

Output strictly in this JSON format mapping each Article ID to its analysis:
{{
  "art_1": {{
    "korean_title": "Translated and editorialized headline in natural Korean",
    "summary_3_lines": [
      "Core factual takeaway 1 in Korean",
      "Core factual takeaway 2 in Korean",
      "Core factual takeaway 3 in Korean"
    ],
    "business_insight": "Concrete business, tech, or market implication in Korean (1-2 sentences)."
  }}
}}
Ensure EVERY article ID from art_1 to art_{len(batch_candidates)} is included in the JSON root object.
"""
    return prompt.strip()

def validate_batch_response(expected_ids, response_text):
    """
    Validates exact ID-set match and required fields in LLM response.
    Returns (is_valid, parsed_dict_or_error_msg).
    """
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    else:
        cleaned = cleaned.strip('` \njson')

    try:
        data = json.loads(cleaned)
    except Exception as e:
        return False, f"JSON parse failure: {e}"

    if not isinstance(data, dict):
        return False, "Response root is not a JSON object"

    # Exact ID-set validation
    received_ids = set(data.keys())
    missing_ids = set(expected_ids) - received_ids
    if missing_ids:
        return False, f"Missing article IDs in response: {missing_ids}"

    validated_results = {}
    for aid in expected_ids:
        item = data.get(aid)
        if not isinstance(item, dict):
            return False, f"Article {aid} analysis is not an object"

        ktitle = item.get("korean_title")
        summ = item.get("summary_3_lines")
        insight = item.get("business_insight")

        if not ktitle or not isinstance(ktitle, str) or len(ktitle.strip()) == 0:
            return False, f"Article {aid} missing valid korean_title"
        if not summ or not isinstance(summ, list) or len(summ) < 1:
            return False, f"Article {aid} missing valid summary_3_lines"
        if not insight or not isinstance(insight, str) or len(insight.strip()) == 0:
            return False, f"Article {aid} missing valid business_insight"

        validated_results[aid] = {
            "korean_title": ktitle.strip(),
            "summary_3_lines": [str(s).strip() for s in summ],
            "business_insight": insight.strip()
        }

    return True, validated_results

def execute_llm_call(model_name, prompt):
    """
    Executes a single LLM request with bounded timeout.
    """
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        prompt,
        request_options={"timeout": API_TIMEOUT_SECONDS}
    )
    return response.text

def analyze_articles():
    # Force cache invalidation: Purge any previous translated/analyzed articles
    for stale_file in ["src/translated_articles.json", "src/edition_stats.json"]:
        if os.path.exists(stale_file):
            try:
                os.remove(stale_file)
                log(f"[Cache Invalidation] Removed stale analysis cache: {stale_file}")
            except Exception as e:
                log(f"[Cache Invalidation] Warning: Failed to remove {stale_file}: {e}")

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        api_key = api_key.strip()

    if not api_key:
        log("[Critical Error] GEMINI_API_KEY is empty. Please set it in .env or GitHub Secrets.")
        sys.exit(1)

    genai.configure(api_key=api_key)

    try:
        with open("src/articles.json", "r", encoding="utf-8") as f:
            candidates = json.load(f)
    except FileNotFoundError:
        log("[Critical Error] src/articles.json not found. Run fetcher.py first.")
        sys.exit(1)

    if not candidates:
        log("[Critical Error] src/articles.json is empty. No candidates to analyze.")
        sys.exit(1)

    # Group candidates by publisher
    by_publisher = defaultdict(list)
    for c in candidates:
        by_publisher[c.get("media", "Tech Media")].append(c)

    all_analyzed_articles = []
    publisher_status_report = {}
    active_model = PRIMARY_MODEL
    daily_quota_circuit_broken = False

    log(f"Starting bounded batch analysis. Target: {ARTICLES_PER_PUBLISHER} articles/publisher.")
    log(f"Active model: {active_model} | Timeout: {API_TIMEOUT_SECONDS}s | Batch Size: {ARTICLES_PER_PUBLISHER}")

    for publisher in PUBLISHERS:
        media_name = publisher["name"]
        pub_candidates = by_publisher.get(media_name, [])
        target_count = min(len(pub_candidates), ARTICLES_PER_PUBLISHER)

        log(f"\n--- Processing {media_name} ({len(pub_candidates)} candidates in pool) ---")

        if len(pub_candidates) == 0:
            log(f" -> [Shortage] 0 candidates found for {media_name}.")
            publisher_status_report[media_name] = {
                "analyzed": 0,
                "target": ARTICLES_PER_PUBLISHER,
                "candidates_found": 0,
                "status": "source_retrieval_failure"
            }
            continue

        # If circuit breaker already tripped, report quota exhausted immediately
        if daily_quota_circuit_broken:
            log(f" -> [CircuitBreaker] Skipping {media_name} due to active daily quota exhaustion.")
            publisher_status_report[media_name] = {
                "analyzed": 0,
                "target": ARTICLES_PER_PUBLISHER,
                "candidates_found": len(pub_candidates),
                "status": "daily_quota_exhausted"
            }
            continue

        # Prepare batch of top candidates
        batch_slice = pub_candidates[:ARTICLES_PER_PUBLISHER]
        expected_ids = [f"art_{i+1}" for i in range(len(batch_slice))]
        prompt = build_batch_prompt(media_name, batch_slice)

        batch_success = False
        batch_attempt = 0
        last_error_category = None

        while batch_attempt <= MAX_BATCH_RETRIES and not batch_success:
            batch_attempt += 1
            log(f"[{media_name}] Executing Batch Call (Attempt {batch_attempt}/{MAX_BATCH_RETRIES+1}, Model: {active_model}, Items: {len(batch_slice)})...")
            start_t = time.time()

            try:
                resp_text = execute_llm_call(active_model, prompt)
                elapsed = time.time() - start_t
                log(f"[{media_name}] LLM response received in {elapsed:.1f}s. Validating schema...")

                is_valid, parsed_or_err = validate_batch_response(expected_ids, resp_text)
                if is_valid:
                    # Merge LLM results with original candidates
                    for idx, candidate in enumerate(batch_slice):
                        aid = f"art_{idx+1}"
                        merged = dict(candidate)
                        merged.update(parsed_or_err[aid])
                        merged["analyzed_by"] = active_model
                        all_analyzed_articles.append(merged)

                    batch_success = True
                    log(f" -> [Success] {len(batch_slice)}/{len(batch_slice)} articles analyzed and verified.")
                    # Bounded anti-rate-limit sleep
                    time.sleep(RATE_LIMIT_DELAY_SECONDS)
                else:
                    log(f" -> [Warning] Batch schema validation failed: {parsed_or_err}")
                    if batch_attempt <= MAX_BATCH_RETRIES:
                        time.sleep(2.0)

            except Exception as e:
                elapsed = time.time() - start_t
                category, desc = classify_api_error(e)
                last_error_category = category
                log(f" -> [API Error in {elapsed:.1f}s] Category={category}: {desc}")

                # CIRCUIT BREAKER 1: Daily Quota Exhaustion
                if category == ErrorCategory.DAILY_QUOTA_EXHAUSTED:
                    log(f" -> [CircuitBreaker TRIPPED] Daily request quota exhausted. Aborting further requests immediately.")
                    daily_quota_circuit_broken = True
                    break

                # CIRCUIT BREAKER 2: Authentication Error
                if category == ErrorCategory.AUTHENTICATION_ERROR:
                    log(f" -> [FastFail] Authentication error. Halting pipeline.")
                    sys.exit(1)

                # MODEL UNAVAILABLE: Switch to fallback model once if primary failed
                if category == ErrorCategory.MODEL_UNAVAILABLE:
                    if active_model != FALLBACK_MODEL:
                        log(f" -> [ModelFallback] Switching active model from {active_model} to {FALLBACK_MODEL}.")
                        active_model = FALLBACK_MODEL
                        time.sleep(1.0)
                        continue
                    else:
                        log(f" -> [Critical] Fallback model {FALLBACK_MODEL} also unavailable.")
                        break

                # TRANSIENT RATE LIMIT: Bounded retry
                if category == ErrorCategory.TRANSIENT_RATE_LIMIT:
                    if batch_attempt <= MAX_BATCH_RETRIES:
                        log(f" -> [Backoff] Waiting 15s before single retry attempt...")
                        time.sleep(15.0)
                    else:
                        break

                # TRANSIENT SERVER ERROR / TIMEOUT
                if category == ErrorCategory.TRANSIENT_SERVER_ERROR:
                    if batch_attempt <= MAX_BATCH_RETRIES:
                        log(f" -> [Backoff] Server error/timeout. Retrying in 5s...")
                        time.sleep(5.0)
                    else:
                        break

        # Record publisher status
        if batch_success:
            status_code = "completed" if len(batch_slice) >= ARTICLES_PER_PUBLISHER else "candidate_shortage"
            analyzed_cnt = len(batch_slice)
        else:
            if daily_quota_circuit_broken:
                status_code = "daily_quota_exhausted"
            elif last_error_category == ErrorCategory.TRANSIENT_RATE_LIMIT:
                status_code = "rate_limit_exceeded"
            else:
                status_code = "analysis_failure"
            analyzed_cnt = 0

        publisher_status_report[media_name] = {
            "analyzed": analyzed_cnt,
            "target": ARTICLES_PER_PUBLISHER,
            "candidates_found": len(pub_candidates),
            "status": status_code
        }

        # Checkpoint incremental progress to disk
        with open("src/translated_articles.json", "w", encoding="utf-8") as f:
            json.dump(all_analyzed_articles, f, ensure_ascii=False, indent=2)

        with open("src/edition_stats.json", "w", encoding="utf-8") as f:
            json.dump(publisher_status_report, f, ensure_ascii=False, indent=2)

    log(f"\n==========================================")
    log(f"Analysis Finished: {len(all_analyzed_articles)} articles secured across {len(PUBLISHERS)} publishers.")
    for p, stats in publisher_status_report.items():
        log(f"- {p}: {stats['analyzed']}/{stats['target']} (Status: {stats['status']})")

    # If 0 articles analyzed across the ENTIRE run due to quota or failure
    if len(all_analyzed_articles) == 0:
        if daily_quota_circuit_broken:
            log("[Quota Blocked] Zero articles analyzed due to Google Gemini Free Tier daily quota exhaustion.")
            # Exit with code 2 so pipeline knows quota was exhausted
            sys.exit(2)
        else:
            log("[Critical Error] Failed to analyze any articles. Exiting.")
            sys.exit(1)

    log("[Success] Final analysis saved to src/translated_articles.json.")

if __name__ == "__main__":
    analyze_articles()
