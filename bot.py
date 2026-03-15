import os
import requests
import time
from flask import Flask
from threading import Thread

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route("/")
def home():
    return "bot running"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

def news_loop():
    while True:
        send_message("🌍 Global News Test\nSystem running successfully")
        time.sleep(60)

def start_news():
    t = Thread(target=news_loop)
    t.start()

if __name__ == "__main__":
    start_news()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
