import os
import time
import requests

print("🔥 程序开始运行")

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

print("✅ 读取环境变量成功")

def send_test():
    print("👉 准备发送消息")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": "机器人正在运行..."
    }
    r = requests.post(url, data=data)
    print("✅ 发送结果:", r.text)

print("🚀 进入主循环")

while True:
    try:
        send_test()
    except Exception as e:
        print("❌ 报错:", e)
    time.sleep(60)
