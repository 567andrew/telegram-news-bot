import time
import requests
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg
    })
    print("发送结果:", r.text)

print("🔥 程序启动成功")

while True:
    try:
        print("🔄 正在运行...")
        send("✅ Worker 正常运行")
    except Exception as e:
        print("❌ 错误:", e)

    time.sleep(60)
