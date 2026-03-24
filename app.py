import os
import time
import requests
import feedparser

print("🔥 新闻机器人启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

sent_links = set()

while True:
    print("🔄 检查新闻")

    try:
        feed = feedparser.parse("https://rss.cnn.com/rss/edition.rss")

        for entry in feed.entries[:3]:
            if entry.link not in sent_links:
                send("📰 " + entry.title)
                sent_links.add(entry.link)
                print("✅ 已发送:", entry.title)
                break

    except Exception as e:
        print("❌ 错误:", e)

    time.sleep(30)
