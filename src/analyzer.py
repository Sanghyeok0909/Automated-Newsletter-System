import json
import time
import os
import sys
from collections import defaultdict
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import ARTICLES_PER_PUBLISHER, PUBLISHERS

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEY.strip()

if not GEMINI_API_KEY:
    print("[Error] GEMINI_API_KEY is empty. Please set it in .env file or GitHub Secrets.", file=sys.stderr)
    sys.exit(1)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Multi-Model Automatic Fallback Pool
FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest"
]

current_model_idx = 0

def call_gemini_with_fallback(prompt):
    global current_model_idx
    last_error = None

    attempts = len(FALLBACK_MODELS)
    for _ in range(attempts):
        model_name = FALLBACK_MODELS[current_model_idx]
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text, model_name
        except Exception as e:
            last_error = e
            err_msg = str(e)
            print(f" -> [Warning] Model '{model_name}' failed ({err_msg[:80]}...).")
            # Rotate to next model in fallback pool
            current_model_idx = (current_model_idx + 1) % len(FALLBACK_MODELS)
            next_model = FALLBACK_MODELS[current_model_idx]
            print(f" -> [Fallback] Switching active model to '{next_model}'.")
            time.sleep(2)

    raise RuntimeError(f"All candidate models in pool failed. Last error: {last_error}")

def analyze_single_article(article):
    """
    Analyzes and translates a single article candidate into Korean editorial format.
    Returns (success_bool, result_dict_or_error, used_model).
    """
    prompt = f"""
    You are an elite tech analyst and editor for a premium daily briefing newsletter.
    Read the following article metadata and provide an objective, high-density structured JSON response in Korean.
    Do not use markdown blocks (like ```json) in the output, just return the raw JSON object.

    Publisher: {article.get('media')}
    Title: {article.get('title')}
    Summary: {article.get('summary')}

    Output strictly in this JSON schema:
    {{
        "korean_title": "Translated and editorialized headline in natural Korean",
        "summary_3_lines": [
            "Core factual takeaway 1 in Korean",
            "Core factual takeaway 2 in Korean",
            "Core factual takeaway 3 in Korean"
        ],
        "business_insight": "Concrete business, tech, or market implication in Korean (1-2 sentences)."
    }}
    """
    try:
        response_text, used_model = call_gemini_with_fallback(prompt)
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.strip("`")
            if cleaned_text.startswith("json"):
                cleaned_text = cleaned_text[4:].strip()
        else:
            cleaned_text = cleaned_text.strip('` \njson')

        parsed_json = json.loads(cleaned_text)

        # Validate schema fields
        if not parsed_json.get("korean_title") or not parsed_json.get("summary_3_lines"):
            return False, "Incomplete schema from model", used_model

        return True, parsed_json, used_model
    except Exception as e:
        return False, str(e), None

def analyze_articles():
    try:
        with open("src/articles.json", "r", encoding="utf-8") as f:
            candidates = json.load(f)
    except FileNotFoundError:
        print("[Error] articles.json not found. Run fetcher.py first.", file=sys.stderr)
        sys.exit(1)

    if not candidates:
        print("[Error] articles.json is empty. No articles to analyze.", file=sys.stderr)
        sys.exit(1)

    # Group candidates by publisher
    by_publisher = defaultdict(list)
    for c in candidates:
        by_publisher[c.get("media", "Tech Media")].append(c)

    analyzed_data = []
    publisher_status_report = {}

    print(f"Starting analysis with target of {ARTICLES_PER_PUBLISHER} articles per publisher...")
    print(f"Total candidates in pool: {len(candidates)} across {len(by_publisher)} sources.")

    for publisher in PUBLISHERS:
        media_name = publisher["name"]
        pub_candidates = by_publisher.get(media_name, [])
        print(f"\n--- Processing {media_name} ({len(pub_candidates)} candidates available) ---")

        if len(pub_candidates) == 0:
            print(f" -> [Shortage] 0 candidates found for {media_name}.")
            publisher_status_report[media_name] = {
                "analyzed": 0,
                "target": ARTICLES_PER_PUBLISHER,
                "candidates_found": 0,
                "status": "source_retrieval_failure"
            }
            continue

        pub_successes = []
        failures_count = 0

        for candidate in pub_candidates:
            if len(pub_successes) >= ARTICLES_PER_PUBLISHER:
                break

            print(f"[{len(pub_successes)+1}/{ARTICLES_PER_PUBLISHER}] Analyzing: {candidate['title'][:60]} (Score: {candidate.get('score', 0)})")

            success, result_or_err, used_model = analyze_single_article(candidate)
            if success:
                merged = dict(candidate)
                merged.update(result_or_err)
                merged["analyzed_by"] = used_model
                pub_successes.append(merged)
                print(f" -> [Success] Analyzed via {used_model}")
                # Rate limit pause: 4s between LLM calls
                time.sleep(4)
            else:
                failures_count += 1
                print(f" -> [Warning] Analysis failed for candidate: {result_or_err}. Attempting next ranked backup candidate...")
                time.sleep(2)

        analyzed_data.extend(pub_successes)

        # Distinguish shortfall reason
        if len(pub_successes) >= ARTICLES_PER_PUBLISHER:
            status_code = "completed"
        elif len(pub_candidates) < ARTICLES_PER_PUBLISHER:
            status_code = "candidate_shortage"
        else:
            status_code = "analysis_failure"

        publisher_status_report[media_name] = {
            "analyzed": len(pub_successes),
            "target": ARTICLES_PER_PUBLISHER,
            "candidates_found": len(pub_candidates),
            "analysis_failures": failures_count,
            "status": status_code
        }
        print(f" -> Finished {media_name}: {len(pub_successes)}/{ARTICLES_PER_PUBLISHER} articles secured (Status: {status_code}).")

    # Fail-fast if literally zero articles across all sources
    if len(analyzed_data) == 0:
        print("[Critical Error] Failed to analyze any articles across all publishers. Aborting pipeline.", file=sys.stderr)
        sys.exit(1)

    # Save final analyzed payload
    with open("src/translated_articles.json", "w", encoding="utf-8") as f:
        json.dump(analyzed_data, f, ensure_ascii=False, indent=2)

    with open("src/edition_stats.json", "w", encoding="utf-8") as f:
        json.dump(publisher_status_report, f, ensure_ascii=False, indent=2)

    print(f"\n==========================================")
    print(f"Analysis Complete: {len(analyzed_data)} articles across {len(PUBLISHERS)} publishers.")
    for p, stats in publisher_status_report.items():
        print(f"- {p}: {stats['analyzed']}/{stats['target']} (Candidates: {stats['candidates_found']}, Status: {stats['status']})")
    print(f"Payload saved to src/translated_articles.json.")

if __name__ == "__main__":
    analyze_articles()
