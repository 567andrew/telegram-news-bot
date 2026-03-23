import requests
import os
import time

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

# 主程序（核心）
def main():
    print("🔥 Bot started")

    while True:
        print("📰 Sending news...")
        send_message("📰 自动新闻测试：" + time.strftime("%H:%M:%S"))
        time.sleep(30)

# 启动
if __name__ == "__main__":
    main()
