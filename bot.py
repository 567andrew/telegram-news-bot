import time
import requests
import os

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_test():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": "机器人运行中..."
    }
    requests.post(url, data=data)

print("机器人启动成功")

while True:
    print("发送测试消息...")
    send_test()
    print("发送完成，等待60秒")
    time.sleep(60)

