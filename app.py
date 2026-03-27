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

# ===== 初始化 =====
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI OK")
    except:
        print("❌ OpenAI 初始化失败")

# ===== RSS =====
RSS_LIST = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

sent_links = set()

# ===== AI智库生成 =====
def generate_briefing(title, summary):

    if not client:
        return f"【简报】{title}"

    try:
        print("🤖 AI处理中...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""
你是全球顶级智库分析师，请把新闻整理成中文简报：

要求：
1. 中文标题（有判断）
2. 3句话总结（有逻辑）
3. 不要逐句翻译

新闻：
标题：{title}
内容：{summary}
"""
            }]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ AI失败:", e)

        # 👉 保底中文（绝对不再发纯英文）
        return f"【简报】{title}"

# ===== 发送 =====
def send(text, source):
    try:
        final_text = f"""
🧠 世界智库简报

{text}

—— 来源：{source}
—— 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": final_text[:4000]
        }, timeout=10)

        print("✅ 已发送")

    except Exception as e:
        print("❌ 发送失败:", e)

# ===== 主循环 =====
def run():
    print("🚀 系统运行中")

    while True:
        try:
            print("🔄 新一轮")

            for rss in RSS_LIST:

                feed = feedparser.parse(rss)

                if not feed.entries:
                    continue

                for entry in feed.entries[:2]:

                    title = entry.title
                    link = entry.link
                    summary = entry.get("summary", "")

                    if link in sent_links:
                        continue

                    print("📰:", title)

                    text = generate_briefing(title, summary)

                    source = "NYT" if "nytimes" in rss else "BBC"

                    send(text, source)

                    sent_links.add(link)

                    time.sleep(3)

            time.sleep(30)

        except Exception as e:
            print("❌ 主循环错误:", e)
            time.sleep(10)

# ===== 启动 =====
if __name__ == "__main__":
    send("🚨 智库系统已启动", "SYSTEM")
    run()
