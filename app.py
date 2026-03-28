import time
import requests
import feedparser
import os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

DATA_FILE = "/opt/render/project/src/data/sent_links.txt"


def load_sent_links():
    if not os.path.exists(DATA_FILE):
        return set()
    with open(DATA_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_sent_link(link):
    with open(DATA_FILE, "a") as f:
        f.write(link + "\n")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def fetch_news():
    news_list = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            news_list.append({
                "title": entry.title,
                "link": entry.link
            })
    return news_list


def main():
    print("🚀 持续运行模式启动")

    sent_links = load_sent_links()
    last_day = datetime.now().day

    while True:
        try:
            now = datetime.now()

            # 每天清空
            if now.day != last_day:
                open(DATA_FILE, "w").close()
                sent_links.clear()
                last_day = now.day
                print("🧹 已清空")

            print("🔍 扫描中...")

            news_list = fetch_news()

            for news in news_list:
                if news["link"] not in sent_links:
                    send_telegram(f"📰 {news['title']}\n{news['link']}")
                    sent_links.add(news["link"])
                    save_sent_link(news["link"])
                    print("✅ 发送:", news["title"])
                    time.sleep(2)

            print("⏱ 等待2分钟")
            time.sleep(120)

        except Exception as e:
            print("❌ 错误:", e)
            time.sleep(10)


if __name__ == "__main__":
    main()
