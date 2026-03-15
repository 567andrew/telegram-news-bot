from flask import Flask
import requests
import feedparser
import html
import threading
import time

TOKEN = "8233133696:AAErhEUJdRf3MGib6FRJO2tHAMvLDipkqto"
CHAT_ID = "7502932042"

feeds = {
    "CNN": "https://rss.cnn.com/rss/edition.rss",
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "GOOGLE": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
}

sent_titles = set()

app = Flask(__name__)


def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })


def clean_title(title):

    title = html.unescape(title)

    if " - " in title:
        title = title.split(" - ")[0]

    return title


def fetch_news():

    for source, url in feeds.items():

        feed = feedparser.parse(url)

        if len(feed.entries) == 0:
            continue

        for entry in feed.entries[:2]:

            title = clean_title(entry.title)

            if title in sent_titles:
                continue

            sent_titles.add(title)

            message = f"""
🌍 {source}

{title}

{entry.link}
"""

            send_message(message)


def news_loop():

    while True:

        print("Checking news...")

        fetch_news()

        time.sleep(300)


@app.route("/")
def home():
    return "News bot running"


if __name__ == "__main__":

    thread = threading.Thread(target=news_loop)
    thread.start()

    app.run(host="0.0.0.0", port=10000)
