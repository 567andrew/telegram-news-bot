import os
import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = "你的BOT_TOKEN"
CHAT_ID = "@world_monitor_news"

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
