import requests
import os
import time
import threading
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ================= 发消息 =================
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

# ================= 自动发新闻 =================
def auto_news():
    while True:
        print("正在发送新闻...")
        send_message("📰 自动新闻测试：" + time.strftime("%H:%M:%S"))
        time.sleep(30)

# 🚀 启动线程（关键！！！）
threading.Thread(target=auto_news, daemon=True).start()

# ================= 测试接口 =================
@app.route("/test")
def test():
    send_message("✅ 测试成功！")
    return "ok"

# ================= 启动 =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
