import time
import requests
import feedparser
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_LIST = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

sent = set()

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def get_news():
    result = []
    for url in RSS_LIST:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            if entry.link not in sent:
                sent.add(entry.link)
                result.append(entry.title + "\n" + entry.link)
    return result


def run():
    print("🔥 程序启动成功")

    while True:
        try:
            print("🔄 抓新闻...")

            news = get_news()

            for n in news:
                send_telegram("📰 " + n)

            print(f"✅ 本轮发送 {len(news)} 条")

            time.sleep(60)

        except Exception as e:
            print("❌ 错误:", e)
            time.sleep(10)


if __name__ == "__main__":
    run()
