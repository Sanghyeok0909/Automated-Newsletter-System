import json
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (HITL Step Required)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEY.strip()

if not GEMINI_API_KEY:
    raise ValueError("[Error] GEMINI_API_KEY is empty. Please open .env file and paste your API key.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Zero-Capital Directive: Use the efficient Flash model (gemini-flash-latest / fallback to gemini-1.5-flash)
try:
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception:
    model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_articles():
    try:
        with open("src/articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("articles.json not found. Run fetcher.py first.")
        return

    analyzed_data = []
    print(f"Starting LLM analysis of {len(articles)} articles...")

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
            response = model.generate_content(prompt)
            # Safely strip markdown formatting if the model unexpectedly adds it
            response_text = response.text.strip()
            if response_text.startswith("```"):
                response_text = response_text.strip("`")
                if response_text.startswith("json"):
                    response_text = response_text[4:].strip()
            else:
                response_text = response_text.strip('` \njson')
            result = json.loads(response_text)
            
            # Merge LLM output with original article data
            article.update(result)
            analyzed_data.append(article)
            
            # Anti-Rate-Limit: 4 seconds delay to stay under 15 RPM Free Tier limit
            time.sleep(4)
            
        except Exception as e:
            print(f"[Warning] Error analyzing article '{article['title']}': {e}")
            
    with open("src/translated_articles.json", "w", encoding="utf-8") as f:
        json.dump(analyzed_data, f, ensure_ascii=False, indent=2)
        
    print(f"Analysis complete. {len(analyzed_data)} articles saved to src/translated_articles.json.")

if __name__ == "__main__":
    analyze_articles()
