import requests
import os
import feedparser
import time
from datetime import datetime
from openai import OpenAI

# ================= 配置 =================
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# RSS源（可以换）
RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"

# 已发送新闻（去重）
sent_links = set()

# ================= 发送消息 =================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

# ================= AI总结 =================
def ai_summary(title, link):
    prompt = f"""
请把下面新闻翻译成中文，并用3句话总结，简洁清晰：

标题: {title}
链接: {link}

输出格式：
【标题】
【总结】
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI总结失败: {e}"

# ================= 提取图片 =================
def get_image(entry):
    if "media_content" in entry:
        return entry.media_content[0]["url"]
    if "links" in entry:
        for link in entry.links:
            if link.type and "image" in link.type:
                return link.href
    return None

# ================= 主逻辑 =================
def fetch_news():
    feed = feedparser.parse(RSS_URL)
    news_list = []

    for entry in feed.entries[:5]:  # 每次最多5条
        link = entry.link

        if link in sent_links:
            continue

        sent_links.add(link)

        title = entry.title
        image = get_image(entry)

        summary = ai_summary(title, link)

        message = f"""
📰 <b>新闻更新</b>

{summary}

🔗 <a href="{link}">阅读原文</a>
"""

        news_list.append((message, image))

    return news_list

# ================= 主循环 =================
def main():
    print("🚀 新闻机器人启动成功")

    while True:
        try:
            news_items = fetch_news()

            for msg, img in news_items:
                if img:
                    # 发送带图片
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                    data = {
                        "chat_id": CHAT_ID,
                        "photo": img,
                        "caption": msg,
                        "parse_mode": "HTML"
                    }
                    requests.post(url, data=data)
                else:
                    send_message(msg)

                time.sleep(2)  # 防止限流

            print(f"✅ 本轮完成：{datetime.now()}")

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(60)  # 每分钟检查一次

# ================= 启动 =================
if __name__ == "__main__":
    main()
