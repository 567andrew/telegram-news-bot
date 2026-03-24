import requests
import feedparser
import time
import os

print("🔥 程序启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ 环境变量错误")
    exit()

RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

def run():
    print("🚀 开始运行")

    while True:
        try:
            print("📡 获取新闻...")
            feed = feedparser.parse(RSS_URL)

            for entry in feed.entries[:3]:
                message = f"{entry.title}\n{entry.link}"
                send_telegram(message)
                print("✅ 已发送:", entry.title)

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(60)

if __name__ == "__main__":
    run()
