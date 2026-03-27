import requests
import feedparser
import time
import os
from datetime import datetime
from openai import OpenAI

print("🔥 快速版智库系统启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ===== OpenAI =====
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI OK")
except Exception as e:
    print("❌ OpenAI失败:", e)
    client = None

# ===== 稳定RSS =====
RSS_LIST = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
]

sent_links = set()

# ===== AI（只处理重要内容）=====
def generate_briefing(title, summary):
    if not client:
        return title, summary[:200]

    try:
        print("🤖 AI处理中...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"用中文总结并给出简短分析：{title}\n{summary}"
            }],
            timeout=15
        )

        content = response.choices[0].message.content.strip()

        return title, content

    except Exception as e:
        print("❌ AI失败:", e)
        return title, summary[:200]

# ===== Telegram =====
def send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        r = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text[:1000]
            },
            timeout=10
        )

        print("📡 返回:", r.text)

    except Exception as e:
        print("❌ 发送失败:", e)

# ===== 主程序 =====
def run():
    print("🚀 run() 已进入")

    while True:
        try:
            print("🔄 新一轮开始")

            for rss in RSS_LIST:
                print("🌐 抓取:", rss)

                feed = feedparser.parse(rss)

                print("📊 条数:", len(feed.entries))

                if not feed.entries:
                    continue

                for i, entry in enumerate(feed.entries[:2]):
                    title = entry.title
                    link = entry.link
                    summary = entry.get("summary", "")

                    if link in sent_links:
                        continue

                    print("📰:", title)

                    # ===== 核心逻辑（快 + 稳）=====
                    if i == 0:
                        # 第一条用AI（高质量）
                        ai_title, ai_content = generate_briefing(title, summary)
                    else:
                        # 第二条直接发（保证速度）
                        ai_title = title
                        ai_content = summary[:150]

                    date = datetime.now().strftime("%Y-%m-%d")

                    message = f"""🧠 {ai_title}

{ai_content}

——
来源：BBC / NYT
时间：{date}
"""

                    send(message)

                    sent_links.add(link)

                    print("✅ 已发送")

                    time.sleep(2)   # ⚡ 加快

            print("⏱️ 等待30秒...")
            time.sleep(30)   # ⚡ 加快

        except Exception as e:
            print("❌ 主循环错误:", e)
            time.sleep(10)

# ===== 启动 =====
if __name__ == "__main__":
    print("🔥 主入口启动")
    run()
