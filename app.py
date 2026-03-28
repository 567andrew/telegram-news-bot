import time
import feedparser
import requests
import os

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
# 📁 存储路径（关键）
# ========================
FILE_PATH = "/data/sent_news.txt"

# ========================
# 📁 去重存储
# ========================
def load_sent_news():
    try:
        if not os.path.exists(FILE_PATH):
            return set()
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    except Exception as e:
        print("读取失败:", e)
        return set()

def save_sent_news(sent_set):
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            for item in sent_set:
                f.write(item + "\n")
    except Exception as e:
        print("保存失败:", e)

# ========================
# 🌐 翻译（免费版）
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
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code != 200:
            print("发送失败:", r.text)
    except Exception as e:
        print("发送异常:", e)

# ========================
# 🧠 主逻辑
# ========================
def run():
    print("🔥 程序启动成功")
    print(f"📁 使用存储路径: {FILE_PATH}")

    sent_news = load_sent_news()
    print(f"📊 已记录新闻数量: {len(sent_news)}")

    while True:
        print("\n🔄 新一轮开始")

        new_count = 0

        for feed_url in RSS_FEEDS:
            print(f"📡 抓取: {feed_url}")

            try:
                feed = feedparser.parse(feed_url)
                entries = feed.entries[:5]
            except Exception as e:
                print("RSS解析失败:", e)
                continue

            for item in entries:
                link = item.link.strip()

                # ✅ 去重核心
                if link in sent_news:
                    continue

                title = item.title
                summary = item.summary if "summary" in item else ""

                # 翻译
                zh_title = translate(title)
                zh_summary = translate(summary[:100])

                message = f"""
🧠 <b>世界智库简报</b>
━━━━━━━━━━━━━━

📰 <b>{zh_title}</b>

📌 {zh_summary}

🔗 <a href="{link}">查看原文</a>
"""

                send_telegram(message)

                sent_news.add(link)
                new_count += 1

                print(f"✅ 已发送: {title}")

        # 保存去重记录
        save_sent_news(sent_news)

        print(f"📊 本轮新增: {new_count}")
        print(f"💾 当前总记录: {len(sent_news)}")
        print(f"⏳ 等待 {CHECK_INTERVAL} 秒...\n")

        time.sleep(CHECK_INTERVAL)

# ========================
# 🚀 启动
# ========================
if __name__ == "__main__":
    run()
