import os
import requests
import feedparser
import json
from datetime import datetime
from google import genai

# Setup Gemini API using the new Google GenAI library
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1. Fetch Sports News from RSS Feeds
RSS_FEEDS = [
    "http://www.espn.com/espn/rss/news",
    "http://feeds.bbci.co.uk/sport/rss.xml"
]

raw_news = []
for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:5]: # Take top stories
        raw_news.append({
            "title": entry.title,
            "link": entry.link,
            "summary": getattr(entry, 'summary', '')
        })

# 2. Ask Gemini AI to summarize into structured HTML
prompt = f"""
You are a sports editor. I will give you raw sports news.
Summarize the top 6 most interesting stories.

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
{json.dumps(raw_news)}
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
)
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
