import requests
import feedparser
import time
import os
from openai import OpenAI

print("🔥 程序启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

def ai_process(text):
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "你是新闻助手"},
                {"role": "user", "content": f"总结并翻译这条新闻成中文：{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI错误:", e)
        return "（AI总结失败）"

def run():
    print("🚀 开始运行")

    while True:
        try:
            print("📡 获取新闻...")
            feed = feedparser.parse(RSS_URL)

            for entry in feed.entries[:2]:
                title = entry.title
                link = entry.link

                ai_text = ai_process(title)

                message = f"""📰 {title}

🌐 {link}

🤖 AI总结：
{ai_text}
"""

                send_telegram(message)
                print("✅ 已发送:", title)

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(120)

if __name__ == "__main__":
    run()
