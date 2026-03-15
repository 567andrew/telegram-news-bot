import os
import requests
import time
from flask import Flask
import threading

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

def news_loop():
    while True:
        print("BOT LOOP RUNNING")
        send_message("Andrew test message")
        time.sleep(60)

@app.route("/")
def home():
    return "bot running"

if __name__ == "__main__":
    thread = threading.Thread(target=news_loop)
    thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
