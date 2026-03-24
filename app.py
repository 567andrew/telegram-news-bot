import os
import time
import requests
import feedparser

print("🔥 程序启动")

# ================== 环境变量 ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

print("✅ 环境变量检查:")
print("BOT_TOKEN:", "OK" if BOT_TOKEN else "❌")
print("CHAT_ID:", "OK" if CHAT_ID else "❌")
print("OPENAI:", "OK" if OPENAI_API_KEY else "❌")

if not BOT_TOKEN or not CHAT_ID or not OPENAI_API_KEY:
    print("❌ 环境变量缺失，程序退出")
    exit(1)

# ================== 延迟导入 OpenAI（防卡死） ==================
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI 初始化成功")
except Exception as e:
    print("❌ OpenAI 初始化失败:", e)
    client = None

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
            "parse_mode": "HTML"
        }
        r = requests.post(url, data=data, timeout=10)
        print("📨 Telegram状态:", r.status_code)
    except Exception as e:
        print("❌ Telegram错误:", e)

# ================== AI处理 ==================
def ai_process(text):
    if not client:
        return "（AI不可用）"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "翻译并总结新闻为中文，50字以内"},
                {"role": "user", "content": text}
            ],
            timeout=15
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
            print("❌ 没有新闻")
            return None

        for entry in feed.entries[:5]:
            if entry.link not in sent_links:
                return entry

        return None

    except Exception as e:
        print("❌ RSS错误:", e)
        return None

# ================== 主循环 ==================
print("🚀 开始主循环")

while True:
    print("🔄 心跳：程序运行中")

    try:
        news = fetch_news()

        if news:
            print("📰 新新闻:", news.title)

            content = news.title + "\n" + news.summary

            ai_text = ai_process(content)

            if ai_text:
                message = f"<b>{news.title}</b>\n\n{ai_text}\n\n{news.link}"
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
