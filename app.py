import time
import requests
import feedparser
import os
from datetime import datetime

# =============================
# 配置
# =============================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

DATA_FILE = "/opt/render/project/src/data/sent_links.txt"

# =============================
# 读取记录
# =============================

def load_sent_links():
    if not os.path.exists(DATA_FILE):
        return set()

    with open(DATA_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


# =============================
# 保存记录
# =============================

def save_sent_link(link):
    with open(DATA_FILE, "a") as f:
        f.write(link + "\n")


# =============================
# 清空文件（关键）
# =============================

def clear_file():
    with open(DATA_FILE, "w") as f:
        f.write("")
    print("🧹 已清空历史记录")


# =============================
# 发送消息
# =============================

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)


# =============================
# 抓新闻
# =============================

def fetch_news():
    news_list = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:5]:
                news_list.append({
                    "title": entry.title,
                    "link": entry.link
                })

        except Exception as e:
            print("❌ 抓取失败:", feed_url, e)

    return news_list


# =============================
# 主程序
# =============================

def main():
    print("🚀 启动（自动清空版）")

    sent_links = load_sent_links()
    last_clear_day = datetime.now().day

    while True:
        try:
            now = datetime.now()

            # 🧹 每天清空一次
            if now.day != last_clear_day:
                clear_file()
                sent_links.clear()
                last_clear_day = now.day

            print("🔍 扫描新闻...")

            news_list = fetch_news()

            for news in news_list:
                if news["link"] not in sent_links:
                    msg = f"📰 {news['title']}\n{news['link']}"

                    send_telegram(msg)

                    sent_links.add(news["link"])
                    save_sent_link(news["link"])

                    print("✅ 已发送:", news["title"])

                    time.sleep(2)

            print("⏱ 等待下一轮...")
            time.sleep(120)

        except Exception as e:
            print("❌ 错误:", e)
            time.sleep(10)


# =============================
# 启动
# =============================

if __name__ == "__main__":
    main()
