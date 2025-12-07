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
        headers={"Authorization": f"Bearer {GROQ_KEY}"},
        json={
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return res.json()["choices"][0]["message"]["content"]

def post_to_x(tweet):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://x.com/login")
        page.fill("input[name='text']", os.getenv("X_EMAIL"))
        page.keyboard.press("Enter")
        time.sleep(2)
        page.fill("input[name='password']", os.getenv("X_PASSWORD"))
        page.keyboard.press("Enter")
        time.sleep(5)
        page.fill("div[role='textbox']", tweet)
        page.click("div[data-testid='tweetButton']")
        time.sleep(3)
        browser.close()

title, summary, link, cat = get_news()
tweet = rewrite(title, summary) + f" {link}"
post_to_x(tweet)
