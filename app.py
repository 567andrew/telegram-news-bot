import os
import time
import requests
import feedparser
from openai import OpenAI

# ================== 启动日志 ==================
print("🔥 程序启动成功")

# ================== 环境变量 ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not BOT_TOKEN or not CHAT_ID or not OPENAI_API_KEY:
    print("❌ 环境变量缺失！")
    print("BOT_TOKEN:", BOT_TOKEN)
    print("CHAT_ID:", CHAT_ID)
    print("OPENAI_API_KEY:", OPENAI_API_KEY)
    exit(1)

# ================== OpenAI ==================
client = OpenAI(api_key=OPENAI_API_KEY)

# ================== RSS ==================
RSS_URL = "https://rss.cnn.com/rss/edition.rss"

# 防重复
sent_links = set()

# ================== Telegram ==================
def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        r = requests.post(url, data=data)
        print("📨 发送状态:", r.status_code)
    except Exception as e:
        print("❌ Telegram发送错误:", e)

# ================== AI处理 ==================
def ai_process(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "把新闻翻译成中文并总结，控制在50字以内"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ AI错误:", e)
        return None

# ================== 抓新闻 ==================
def fetch_news():
    try:
        feed = feedparser.parse(RSS_URL)
        if not feed.entries:
            print("❌ 没抓到新闻")
            return None

        for entry in feed.entries[:5]:
            if entry.link not in sent_links:
                return entry

        return None

    except Exception as e:
        print("❌ 抓取错误:", e)
        return None

# ================== 主循环 ==================
while True:
    try:
        print("🔄 正在检查新闻...")

        news = fetch_news()

        if news:
            print("📰 新新闻:", news.title)

            content = news.title + "\n" + news.summary

            ai_text = ai_process(content)

            if ai_text:
                message = f"<b>{news.title}</b>\n\n{ai_text}\n\n<a href='{news.link}'>查看原文</a>"
                send_telegram(message)

                sent_links.add(news.link)
                print("✅ 已发送")
            else:
                print("❌ AI失败")

        else:
            print("⏳ 暂无新新闻")

    except Exception as e:
        print("❌ 主循环错误:", e)

    time.sleep(30)
