import json
import time
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (HITL Step Required)
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
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest"
]

current_model_idx = 0

def call_gemini_with_fallback(prompt):
    global current_model_idx
    last_error = None

    # Try models starting from the current_model_idx
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

def analyze_articles():
    try:
        with open("src/articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("[Error] articles.json not found. Run fetcher.py first.", file=sys.stderr)
        sys.exit(1)

    if not articles:
        print("[Error] articles.json is empty. No articles to analyze.", file=sys.stderr)
        sys.exit(1)

    analyzed_data = []
    print(f"Starting LLM analysis of {len(articles)} articles with Multi-Model Fallback...")

    for i, article in enumerate(articles):
        print(f"[{i+1}/{len(articles)}] Analyzing: {article['title']}")
        
        prompt = f"""
        You are a professional tech analyst and translator. Read the following article summary and provide a structured JSON response.
        Do not use markdown blocks (like ```json) in the output, just return the raw JSON object.
        
        Title: {article['title']}
        Summary: {article['summary']}
        
        Output strictly in this JSON format:
        {{
            "korean_title": "Translated title in natural Korean",
            "summary_3_lines": ["Core point 1 in Korean", "Core point 2 in Korean", "Core point 3 in Korean"],
            "business_insight": "One sentence business or tech insight in Korean."
        }}
        """
        
        try:
            response_text, used_model = call_gemini_with_fallback(prompt)
            
            # Safely strip markdown formatting if the model unexpectedly adds it
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.strip("`")
                if cleaned_text.startswith("json"):
                    cleaned_text = cleaned_text[4:].strip()
            else:
                cleaned_text = cleaned_text.strip('` \njson')
            
            result = json.loads(cleaned_text)
            
            # Merge LLM output with original article data
            article.update(result)
            article["analyzed_by"] = used_model
            analyzed_data.append(article)
            print(f" -> [Success] Analyzed via {used_model}")
            
            # Anti-Rate-Limit: 4 seconds delay to stay under Free Tier RPM limits
            time.sleep(4)
            
        except Exception as e:
            print(f"[Warning] Failed to analyze article '{article['title']}': {e}")

    # Fail-Fast Enforcement: If no articles were analyzed successfully, fail the CI/CD step immediately
    if len(analyzed_data) == 0:
        print(f"[Critical Error] Failed to analyze any of the {len(articles)} articles. Aborting pipeline.", file=sys.stderr)
        sys.exit(1)
            
    with open("src/translated_articles.json", "w", encoding="utf-8") as f:
        json.dump(analyzed_data, f, ensure_ascii=False, indent=2)
        
    print(f"\nAnalysis complete. {len(analyzed_data)}/{len(articles)} articles successfully saved to src/translated_articles.json.")

if __name__ == "__main__":
    analyze_articles()
