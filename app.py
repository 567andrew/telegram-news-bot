import os
import time
import requests

print("🔥 程序启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# 只发送一次
sent = False

while True:
    print("🔄 程序还活着")

    if not sent:
        send("✅ 测试成功：Worker正常运行")
        sent = True
        print("📨 已发送一次")

    time.sleep(10)
