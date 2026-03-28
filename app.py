import time
import feedparser
import requests

# ========================
# 🔑 配置区（必须修改）
# ========================
BOT_TOKEN = "你的BOT_TOKEN"
CHAT_ID = "你的CHAT_ID"

RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

CHECK_INTERVAL = 60  # 每60秒检测一次

# ========================
# 📁 去重存储
# ========================
def load_sent_news():
    try:
        with open("sent_news.txt", "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    except:
        return set()

def save_sent_news(sent_set):
    with open("sent_news.txt", "w", encoding="utf-8") as f:
        for item in sent_set:
            f.write(item + "\n")

# ========================
# 🌐 简单翻译（免费版）
# ========================
def translate(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "zh-CN",
            "dt": "t",
            "q": text
        }
        res = requests.get(url, params=params, timeout=10)
        return res.json()[0][0][0]
    except:
        return text

# ========================
# 📤 发送Telegram
# ========================
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("发送失败:", e)

# ========================
# 🧠 主逻辑
# ========================
def run():
    print("🔥 程序启动成功")
    sent_news = load_sent_news()

    while True:
        print("\n🔄 新一轮开始")

        new_count = 0

        for feed_url in RSS_FEEDS:
            print(f"📡 抓取: {feed_url}")

            feed = feedparser.parse(feed_url)
            entries = feed.entries[:5]  # 只取最新5条

            for item in entries:
                link = item.link.strip()

                # ✅ 去重判断（核心）
                if link in sent_news:
                    continue

                title = item.title
                summary = item.summary if "summary" in item else ""

                # 翻译
                zh_title = translate(title)
                zh_summary = translate(summary[:100])

                message = f"""
🧠 <b>世界智库简报</b>

📰 <b>{zh_title}</b>

{zh_summary}

🔗 <a href="{link}">查看原文</a>
"""

                send_telegram(message)

                # 记录已发送
                sent_news.add(link)
                new_count += 1

                print(f"✅ 已发送: {title}")

        save_sent_news(sent_news)

        print(f"📊 本轮新新闻: {new_count}")
        print(f"⏳ 等待 {CHECK_INTERVAL} 秒...\n")

        time.sleep(CHECK_INTERVAL)

# ========================
# 🚀 启动
# ========================
if __name__ == "__main__":
    run()
