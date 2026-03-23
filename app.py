from flask import Flask
import requests
import os

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

@app.route("/")
def home():
    return "机器人正常运行中！"

@app.route("/test")
def test():
    send_message("测试成功！来自Render网址")
    return "消息已发送！"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
