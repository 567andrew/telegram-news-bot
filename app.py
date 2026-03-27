import requests
import feedparser
import time
import os
from datetime import datetime
from openai import OpenAI

print("🔥 程序启动成功（最外层）")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

print("🔍 BOT_TOKEN:", BOT_TOKEN)
print("🔍 CHAT_ID:", CHAT_ID)
print("🔍 OPENAI_API_KEY:", "有" if OPENAI_API_KEY else "没有")

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI OK")
except Exception as e:
    print("❌ OpenAI失败:", e)
    client = None

RSS_LIST = [
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

sent_links = set()

def send(text):
    print("📤 准备发送")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

    print("📡 返回:", r.text)


def run():
    print("🚀 run() 已进入（关键）")

    while True:
        print("🔄 循环开始")

        for rss in RSS_LIST:
            print("🌐 RSS:", rss)

            feed = feedparser.parse(rss)

            print("📊 数量:", len(feed.entries))

            for entry in feed.entries[:1]:
                title = entry.title
                link = entry.link

                print("📰 新闻:", title)

                if link in sent_links:
                    print("⚠️ 已发送过")
                    continue

                send("测试消息：" + title)

                sent_links.add(link)

                time.sleep(5)

        print("⏳ 等待60秒")
        time.sleep(60)


print("🔥 即将进入 main")

if __name__ == "__main__":
    print("🔥 main 已触发")
    run()
