import os
import time
import requests

print("🔥 程序启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        }, timeout=10)
        print("📨 发送成功")
    except Exception as e:
        print("❌ 发送失败:", e)

sent = False

while True:
    try:
        print("🔄 程序运行中...")

        if not sent:
            send("✅ Worker稳定运行测试")
            sent = True

    except Exception as e:
        print("❌ 主循环错误:", e)

    time.sleep(10)
