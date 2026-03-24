import time
import requests
import os

def send(text):
    TOKEN = os.environ["BOT_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url, json=data)

print("✅ 程序启动成功", flush=True)

while True:
    try:
        print("🔄 正在运行...", flush=True)

        send("✅ Worker 正常运行")

    except Exception as e:
        print("❌ 错误:", e, flush=True)

    time.sleep(60)
