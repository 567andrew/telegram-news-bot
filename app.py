import requests
import feedparser
import time
import os
from datetime import datetime
from openai import OpenAI

print("🔥 Andrew智库系统启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ===== 初始化 =====
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI 已连接")
    except Exception as e:
        print("❌ OpenAI 初始化失败:", e)

# ===== RSS源 =====
RSS_LIST = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

sent_links = set()

# ===== AI智库生成 =====
def generate_briefing(title, summary):

    # ===== 第一层：AI生成 =====
    if client:
        try:
            print("🤖 AI处理中...")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"""
你是全球顶级智库分析师，请整理以下新闻：

要求：
1. 中文标题（有判断）
2. 核心内容（2-3句话，简洁清晰）
3. 不要逐句翻译

新闻：
标题：{title}
内容：{summary}
"""
                }],
                timeout=15
            )

            result = response.choices[0].message.content.strip()

            print("📊 AI返回:", result)

            if result:
                print("✅ AI成功")
                return result

        except Exception as e:
            print("❌ AI失败:", e)

    # ===== 第二层：降级方案（一定是中文）=====
    print("⚠️ 使用降级方案")

    return f"""
【简报】{title}

该事件反映出当前国际局势中的重要变化，可能对相关地区的政治或经济产生持续影响。建议持续关注后续发展。
"""

# ===== Telegram发送 =====
def send(text, source):
    try:
        print("📤 发送中...")

        final_text = f"""
🧠 世界智库简报

{text}

—— 来源：{source}
—— 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        r = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": final_text[:4000]
            },
            timeout=10
        )

        print("📡 Telegram返回:", r.text)

    except Exception as e:
        print("❌ 发送失败:", e)

# ===== 主循环 =====
def run():
    print("🚀 系统运行中")

    while True:
        try:
            print("🔄 新一轮开始")

            for rss in RSS_LIST:
                print("🌐 抓取:", rss)

                feed = feedparser.parse(rss)

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

                    source = "NYT" if "nytimes" in rss else "BBC"

                    send(text, source)

                    sent_links.add(link)

                    time.sleep(3)

            print("⏱️ 等待30秒...")
            time.sleep(30)

        except Exception as e:
            print("❌ 主循环错误:", e)
            time.sleep(10)

# ===== 启动 =====
if __name__ == "__main__":
    print("🔥 主入口启动")

    # 👉 启动提示（确认系统活着）
    try:
        send("🚨 智库系统已启动", "SYSTEM")
    except:
        pass

    run()
