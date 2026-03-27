print("🔥🔥🔥 VERSION 999 🔥🔥🔥")
import requests
import feedparser
import time
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI

# ===== 启动标志（必须有）=====
print("🔥 Andrew系统已启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ===== 高质量信息源 =====
RSS_LIST = [
    "http://feeds.reuters.com/reuters/topNews",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.economist.com/latest/rss.xml",
    "https://www.ft.com/rss/home",
    "https://www.brookings.edu/feed/"
]

# ===== 去重缓存 =====
sent_links = set()
sent_briefings = []
last_reset_day = ""

# ===== 每天清空 =====
def check_reset():
    global sent_links, sent_briefings, last_reset_day

    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    today = now.strftime("%Y-%m-%d")

    if last_reset_day != today:
        sent_links.clear()
        sent_briefings.clear()
        last_reset_day = today
        print("🧹 已清空缓存")

# ===== AI简报生成 =====
def generate_briefing(title, summary):
    prompt = f"""
你是顶级智库编辑，请写中文深度简报：

标题：{title}
内容：{summary}

结构如下：

【核心事件】
一句话总结

【关键事实】
3条

【深层逻辑】
为什么发生

【趋势判断】
未来变化

【影响分析】
对普通人的影响

【一句话结论】
一句总结
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ AI错误:", e)
        return None

# ===== 图片 =====
def get_image(title):
    return f"https://source.unsplash.com/800x600/?{title}"

# ===== 发送 =====
def send_photo(text, image_url):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "photo": image_url,
                "caption": text[:1000]
            }
        )
    except Exception as e:
        print("❌ 发送失败:", e)

# ===== 主程序 =====
def run():
    print("🚀 单条简报系统启动")

    while True:
        check_reset()

        try:
            for rss in RSS_LIST:
                feed = feedparser.parse(rss)

                for entry in feed.entries[:5]:
                    link = entry.link
                    title = entry.title
                    summary = entry.get("summary", "")

                    # ===== 去重 =====
                    if link in sent_links:
                        continue

                    print("📰 处理:", title)

                    briefing = generate_briefing(title, summary)

                    if not briefing or len(briefing) < 80:
                        continue

                    # ===== 内容去重 =====
                    duplicate = False
                    for b in sent_briefings[-20:]:
                        if briefing[:60] in b:
                            duplicate = True
                            break

                    if duplicate:
                        print("⚠️ 重复跳过")
                        continue

                    image = get_image(title)

                    date = datetime.now(
                        ZoneInfo("America/Los_Angeles")
                    ).strftime("%Y-%m-%d")

                    message = f"🧠 全球简报 | {date}\n\n{briefing}"

                    send_photo(message, image)

                    sent_links.add(link)
                    sent_briefings.append(briefing)

                    print("✅ 已发送")

                    time.sleep(10)

        except Exception as e:
            print("❌ 主循环错误:", e)

        time.sleep(600)


# ===== 启动入口（最关键）=====
if __name__ == "__main__":
    run()
