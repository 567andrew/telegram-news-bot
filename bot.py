from flask import Flask
import requests
import os
import feedparser

TOKEN = "8233133696:AAErhEUJdRf3MGib6FRJO2tHAMvLDipkqto"
CHAT_ID = "7502932042"

app = Flask(__name__)

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def send_news_once():
    print("Fetching news...")
    feed = feedparser.parse("https://rss.cnn.com/rss/edition.rss")

    if len(feed.entries) > 0:
        entry = feed.entries[0]
        message = f"🌍 {entry.title}\n{entry.link}"
        print("Sending:", entry.title)
        send_message(message)

@app.route("/")
def home():
    return "News bot running"

if __name__ == "__main__":
    send_news_once()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
