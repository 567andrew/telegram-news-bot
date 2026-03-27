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

# ===== 检查环境变量 =====
if not BOT_TOKEN or not CHAT_ID or not OPENAI_API_KEY:
    print("❌ 环境变量缺失")
else:
    print("✅ 环境变量正常")

# ===== OpenAI =====
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI 初始化成功")
except Exception as e:
    print("❌ OpenAI 初始化失败:", e)
    client = None

# ===== RSS源（换成稳定的）=====
RSS_LIST = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

sent_links = set()

# ===== AI =====
def generate_briefing(title, summary):
    if not client:
        return title

    try:
        print("🤖 调用AI...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"用中文总结：{title}\n{summary}"
            }],
            timeout=20
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ AI失败:", e)
        return title

# ===== Telegram =====
def send(text):
    try:
        print("📤 发送中...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        r = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text[:1000]
            },
            timeout=10
        )

        print("📡 Telegram返回:", r.text)

    except Exception as e:
        print("❌ 发送失败:", e)

# ===== 主程序 =====
def run():
    print("🚀 run() 已进入")

    while True:
        try:
            print("🔄 开始新一轮")

            for rss in RSS_LIST:
                print("🌐 抓取:", rss)

                try:
                    feed = feedparser.parse(rss)
                except Exception as e:
                    print("❌ RSS错误:", e)
                    continue

                print("📊 条数:", len(feed.entries))

                if not feed.entries:
                    print("⚠️ RSS为空")
                    continue

                for entry in feed.entries[:2]:
                    title = entry.title
                    link = entry.link
                    summary = entry.get("summary", "")

                    if link in sent_links:
                        continue

                    print("📰 新闻:", title)

                    text = generate_briefing(title, summary)

                    send(text)

                    sent_links.add(link)

                    time.sleep(5)

            print("⏱️ 等待60秒...")
            time.sleep(60)

        except Exception as e:
            print("❌ 主循环错误:", e)
            time.sleep(10)

# ===== 启动 =====
if __name__ == "__main__":
    print("🔥 主入口启动")
    run()
