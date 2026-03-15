from flask import Flask
import requests
import os
import time
import threading
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

def get_news():
    feed = feedparser.parse("https://rss.cnn.com/rss/edition.rss")
    for entry in feed.entries[:3]:
        message = f"🌍 {entry.title}\n{entry.link}"
        send_message(message)

def news_loop():
    while True:
        try:
            get_news()
        except Exception as e:
            print(e)
        time.sleep(300)

@app.route("/")
def home():
    return "News bot running"

if __name__ == "__main__":
    thread = threading.Thread(target=news_loop)
    thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
