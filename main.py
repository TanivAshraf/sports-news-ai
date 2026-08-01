import os
import requests
import feedparser
import json
import random
import time
from datetime import datetime
from google import genai

# Setup Gemini API using the new Google GenAI library
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1. Fetch Sports News from 4 Multiple RSS Feeds
RSS_FEEDS = [
    "http://www.espn.com/espn/rss/news",
    "http://feeds.bbci.co.uk/sport/rss.xml",
    "https://www.skysports.com/rss/12040",
    "https://sports.yahoo.com/rss/"
]

raw_news = []
for feed_url in RSS_FEEDS:
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]: # Take top stories from each source
            raw_news.append({
                "title": entry.title,
                "link": entry.link,
                "summary": getattr(entry, 'summary', '')
            })
    except Exception as e:
        print(f"Failed to fetch feed {feed_url}: {e}")

# Shuffle slightly to ensure fresh variety on each run
random.shuffle(raw_news)

# 2. Ask Gemini AI to pick the 6 most diverse news stories
prompt = f"""
You are a global sports editor. I will give you raw sports news from multiple sources.
Select the 6 MOST UNIQUE AND DIVERSE news stories across different sports (e.g. Football, Cricket, Basketball, F1, Tennis). Do NOT pick duplicate topics.

Format each story as an HTML block using EXACTLY this structure:
<div class="card">
  <h2>TITLE HERE</h2>
  <ul>
    <li>Bullet point 1</li>
    <li>Bullet point 2</li>
  </ul>
  <a href="LINK HERE" target="_blank" class="btn">Read Full Article &rarr;</a>
</div>

Return ONLY the HTML code blocks for the cards. Do not wrap in ```html codeblocks.

Raw News Data:
{json.dumps(raw_news[:20])}
"""

# Try official aliases from Google AI Studio
candidate_models = [
    'gemini-flash-latest',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
    'gemini-pro-latest'
]

response = None

for model_name in candidate_models:
    try:
        print(f"Attempting model: {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        print(f"SUCCESS! Generated news using model: {model_name}")
        break
    except Exception as e:
        print(f"Model {model_name} failed: {e}")
        time.sleep(2)

if not response or not response.text:
    raise RuntimeError("Failed to generate content with any attempted Gemini model.")

cards_html = response.text.replace("```html", "").replace("```", "")

today_date = datetime.now().strftime("%B %d, %Y")

# 3. Build full website (HTML + Modern CSS)
full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Sports Digest</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 800px;
            width: 100%;
        }}
        header {{
            text-align: center;
            padding: 20px 0 40px;
            border-bottom: 1px solid #334155;
            margin-bottom: 30px;
        }}
        h1 {{ margin: 0; font-size: 2.2rem; color: var(--accent); }}
        .date {{ color: var(--text-muted); font-size: 0.95rem; margin-top: 8px; }}
        .card {{
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            border: 1px solid #334155;
        }}
        .card h2 {{ margin-top: 0; font-size: 1.3rem; color: var(--text); line-height: 1.4; }}
        .card ul {{ padding-left: 20px; color: var(--text-muted); line-height: 1.6; }}
        .card li {{ margin-bottom: 8px; }}
        .btn {{
            display: inline-block;
            background-color: var(--accent);
            color: #0f172a;
            text-decoration: none;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9rem;
            margin-top: 10px;
            transition: background 0.2s;
        }}
        .btn:hover {{ background-color: var(--accent-hover); color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏆 Daily Sports AI Digest</h1>
            <div class="date">Updated on {today_date}</div>
        </header>
        <main>
            {cards_html}
        </main>
    </div>
</body>
</html>
"""

# Save to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("index.html generated successfully!")
