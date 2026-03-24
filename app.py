import requests
import feedparser
import time
import os
from openai import OpenAI

# ========= 配置 =========
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# 新闻源（BBC）
RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"

# ========= 发送Telegram =========
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

# ========= AI处理 =========
def process_news(title, link, summary):
    content = f"{title}\n{summary}"
    content = content[:2000]  # 限制长度省钱

    prompt = f"""
请处理这条新闻：

1. 用中文总结（100字以内）
2. 生成一个吸引人的标题
3. 提取3个关键词

内容：
{content}

返回格式：
标题：
总结：
关键词：
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content

# ========= 主循环 =========
def run():
    print("🚀 新闻机器人启动成功")

    seen = set()

    while True:
        feed = feedparser.parse(RSS_URL)

        for entry in feed.entries[:5]:
            if entry.link in seen:
                continue

            seen.add(entry.link)

            title = entry.title
            summary = entry.summary
            link = entry.link

            try:
                ai_result = process_news(title, link, summary)

                message = f"""
<b>{title}</b>

{ai_result}

<a href="{link}">查看原文</a>
"""
                send_telegram(message)
                print("✅ 已发送:", title)

            except Exception as e:
                print("❌ 出错:", e)

        time.sleep(60)  # 每60秒抓一次

# ========= 启动 =========
if __name__ == "__main__":
    run()
