from flask import Flask
import requests
import os

TOKEN = "你的BOT_TOKEN"
CHAT_ID = "@world_monitor_news"

app = Flask(__name__)

def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    r = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

    print("Telegram response:", r.text)


@app.route("/")
def home():
    return "Bot Running"


@app.route("/test")
def test():

    send_message("机器人测试成功")

    return "Test OK"


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)

