import requests
import feedparser
import time
import os
from datetime import datetime

print("🔥 测试系统启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

RSS_LIST = [
    "http://feeds.reuters.com/reuters/topNews"
]

sent_links = set()

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

    print("📡 Telegram返回:", r.text)


def run():
    while True:
        print("🔄 抓新闻")

        for rss in RSS_LIST:
            feed = feedparser.parse(rss)

            print("📊 数量:", len(feed.entries))

            for entry in feed.entries[:1]:
                title = entry.title
                link = entry.link

                if link in sent_links:
                    continue

                print("📰:", title)

                text = f"""
🧠 测试标题

{title}

——
测试系统
"""

                send(text)

                sent_links.add(link)

                time.sleep(5)

        print("⏳ 等待60秒")
        time.sleep(60)


if __name__ == "__main__":
    run()
