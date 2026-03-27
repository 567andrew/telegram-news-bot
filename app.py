import requests
import feedparser
import time
import os
from datetime import datetime
from openai import OpenAI

print("🔥 Andrew系统启动成功")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ===== 初始化检查 =====
if not BOT_TOKEN or not CHAT_ID or not OPENAI_API_KEY:
    print("❌ 环境变量缺失")
else:
    print("✅ 环境变量正常")

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI 初始化成功")
except Exception as e:
    print("❌ OpenAI 初始化失败:", e)
    client = None

RSS_LIST = [
    "http://feeds.reuters.com/reuters/topNews",
    "http://feeds.bbci.co.uk/news/world/rss.xml"
]

sent_links = set()

# ===== AI =====
def generate_briefing(title, summary):
    if not client:
        return None

    try:
        print("🤖 调用AI中...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"用中文总结：{title}\n{summary}"
            }]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ AI失败:", e)
        return None

# ===== 发送 =====
def send(text):
    try:
        print("📤 正在发送到Telegram...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": text
        }, timeout=10)

        print("📡 Telegram返回:", r.text)

    except Exception as e:
        print("❌ 发送失败:", e)

# ===== 主逻辑 =====
def run():
    print("🚀 run() 已进入")

    while True:
        try:
            print("🔄 开始抓新闻")

            for rss in RSS_LIST:
                print("🌐 RSS:", rss)

                feed = feedparser.parse(rss)

                print("📊 条数:", len(feed.entries))

                for entry in feed.entries[:2]:
                    title = entry.title
                    link = entry.link

                    if link in sent_links:
                        continue

                    print("📰 新闻:", title)

                    summary = entry.get("summary", "")

                    text = generate_briefing(title, summary)

                    if not text:
                        print("⚠️ AI为空，跳过")
                        continue

                    send(text)

                    sent_links.add(link)

                    time.sleep(5)

            print("⏱️ 等待下一轮...")
            time.sleep(60)

        except Exception as e:
            print("❌ 主循环错误:", e)
            time.sleep(10)

# ===== 启动 =====
if __name__ == "__main__":
    print("🔥 主入口启动")
    run()
