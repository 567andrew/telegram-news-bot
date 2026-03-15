from flask import Flask
import requests
import os
import time
import threading
import feedparser

TOKEN = "你的BOT_TOKEN"
CHAT_ID = "你的CHAT_ID"

WEBSITE = "https://telegram-news-bot-pdxd.onrender.com"

app = Flask(__name__)

sent_links = set()

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

    print("Telegram response:", response.text)

def fetch_news():
    print("Checking news...")

    feeds = [
        "https://rss.cnn.com/rss/edition.rss",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://www.reutersagency.com/feed/?best-topics=world&post_type=best"
    ]

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:

            if entry.link in sent_links:
                continue

            sent_links.add(entry.link)

            message = f"""
🌍 {entry.title}

{entry.link}

Source: News
Website: {WEBSITE}
"""

            send_message(message)

def news_loop():
    while True:

        try:
            fetch_news()

        except Exception as e:
            print("Error:", e)

        time.sleep(300)

@app.route("/")
def home():
    return "News bot running"

def start_news_thread():

    thread = threading.Thread(target=news_loop)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":

    start_news_thread()

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
