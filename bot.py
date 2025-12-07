import feedparser
import requests
import time
import os
from playwright.sync_api import sync_playwright

GROQ_KEY = os.getenv("GROQ_API_KEY")

RSS_FEEDS = {
    "AI": "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "Crypto": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Finance": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US"
}

def get_news():
    for cat, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        entry = feed.entries[0]
        return entry.title, entry.summary, entry.link, cat

def rewrite(title, summary):
    prompt = f"""Rewrite this news into a fun, witty X tweet.
Max 240 characters. 1 emoji. No hashtags.

News:
{title}
{summary}
"""

    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",  # ✅ ACTIVE MODEL
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )

    data = res.json()

    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        print("GROQ ERROR:", data)
        return f"{title} 🚀"

def post_to_x(tweet):
    from playwright.sync_api import sync_playwright
    import time
    import os

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 👈 IMPORTANT
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://x.com/login", timeout=60000)
        time.sleep(5)

        page.fill("input[autocomplete='username']", os.getenv("X_EMAIL"))
        page.keyboard.press("Enter")
        time.sleep(5)

        page.fill("input[type='password']", os.getenv("X_PASSWORD"))
        page.keyboard.press("Enter")
        time.sleep(10)

        # Go directly to post box
        page.goto("https://x.com/home", timeout=60000)
        time.sleep(8)

        page.click("div[aria-label='Post']")
        time.sleep(2)

        page.keyboard.type(tweet, delay=20)
        time.sleep(2)

        page.click("div[data-testid='tweetButtonInline']")
        time.sleep(5)

        browser.close()

