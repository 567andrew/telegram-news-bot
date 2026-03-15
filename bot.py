from flask import Flask
import requests
import os
import feedparser

TOKEN = "你的BOT_TOKEN"
CHAT_ID = "7502932042"

WEBSITE = "https://telegram-news-bot-pdxd.onrender.com"

app = Flask(__name__)

def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

    print("Telegram:", response.text)


def fetch_news():

    print("Fetching news...")

    feeds = [
        "https://rss.cnn.com/rss/edition.rss",
        "http://feeds.bbci.co.uk/news/rss.xml"
    ]

    for feed_url in feeds:

        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:2]:

            message = f"""
🌍 {entry.title}

{entry.link}

Source: News
Website: {WEBSITE}
"""

            send_message(message)


@app.route("/")
def home():

    fetch_news()

    return "News sent"


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
