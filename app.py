import requests
import os
import time
from flask import Flask
import threading

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# 发消息
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

# 自动发送
def auto_news():
    print("🔥 自动新闻线程启动成功")
    while True:
        print("📰 正在发送新闻...")
        send_message("📰 自动新闻测试：" + time.strftime("%H:%M:%S"))
        time.sleep(30)

# 👇 用 Flask 启动时触发（关键！！！）
@app.before_first_request
def start_bot():
    threading.Thread(target=auto_news).start()

# 测试接口
@app.route("/test")
def test():
    send_message("✅ 测试成功")
    return "ok"

# 首页（防止Render休眠）
@app.route("/")
def home():
    return "running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
