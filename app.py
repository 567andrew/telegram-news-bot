import requests
import feedparser
import time
import os
from datetime import datetime
from openai import OpenAI

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

RSS_LIST = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    "https://time.com/feed/",
]

sent_links = set()

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def ai_summary(text):
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "你是新闻编辑，请提取核心事实（谁、发生什么、结果），用一句简洁中文表达（30-50字），不要翻译标题"
                },
                {
                    "role": "user",
                    "content": text[:1000]
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except:
        return None

def get_source(url):
    if "bbc" in url:
        return "BBC"
    if "cnn" in url:
        return "CNN"
    if "nytimes" in url:
        return "NYT"
    if "reuters" in url:
        return "REUTERS"
    if "guardian" in url:
        return "GUARDIAN"
    if "time" in url:
        return "TIME"
    return "NEWS"

def run():
    print("🚀 启动成功")

    while True:
        try:
            for rss in RSS_LIST:
                feed = feedparser.parse(rss)

                for entry in feed.entries[:3]:
                    link = entry.link

                    if link in sent_links:
                        continue

                    sent_links.add(link)

                    # ✅ 关键：用全文
                    content = entry.title + " " + entry.get("summary", "")

                    summary = ai_summary(content)
                    if not summary:
                        continue

                    source = get_source(link)
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")

                    message = f"""{summary}

{source} {now}"""

                    send_message(message)

                    print("✅ 已发送:", summary)

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(600)

if __name__ == "__main__":
    run()
