import os
import time
import requests
import feedparser
from openai import OpenAI

# ================== 配置 ==================
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

RSS_URL = "https://rss.cnn.com/rss/edition.rss"

sent_links = set()

# ================== 发送Telegram ==================
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

# ================== AI处理 ==================
def ai_process(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是新闻助手，翻译并总结成简短中文（50字以内）"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("AI错误:", e)
        return None

# ================== 抓新闻 ==================
def fetch_news():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return None

    for entry in feed.entries[:5]:
        if entry.link not in sent_links:
            return entry
    return None

# ================== 主循环 ==================
print("🔥 Worker启动成功")

while True:
    try:
        print("🔄 正在检查新闻...")

        news = fetch_news()

        if news:
            print("📰 找到新闻:", news.title)

            content = news.title + "\n" + news.summary

            ai_text = ai_process(content)

            if ai_text:
                message = f"<b>{news.title}</b>\n\n{ai_text}\n\n<a href='{news.link}'>查看原文</a>"
                send_telegram(message)

                sent_links.add(news.link)

                print("✅ 已发送")
            else:
                print("❌ AI处理失败")

        else:
            print("⏳ 没有新新闻")

    except Exception as e:
        print("主循环错误:", e)

    time.sleep(30)
