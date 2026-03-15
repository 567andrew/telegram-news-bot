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
    r = requests.post(url, data=data)
    print("SEND RESULT:", r.text)

def loop():
    while True:
        print("BOT LOOP RUNNING")
        send_message("Andrew test message")
        time.sleep(60)

def start():
    t = Thread(target=loop)
    t.start()

if __name__ == "__main__":
    start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
