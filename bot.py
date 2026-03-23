import requests
import os
import time

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_test():
    print("🚀 bot started")

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": "✅ 测试成功！机器人正常工作"
    }

    r = requests.post(url, data=data)
    print("📨 status:", r.text)


if __name__ == "__main__":
    send_test()

    while True:
        print("😴 running...")
        time.sleep(60)
