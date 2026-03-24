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

# 🌍 多新闻源
RSS_LIST = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    "https://time.com/feed/",
]

# 🔥 只做“当前运行去重”
sent_links = set()

def send_photo(text, image_url):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": text
    }
    requests.post(url, data=data)

def ai_summary(text):
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "提取新闻核心信息，用简洁中文写一段话（40字以内），不要标题，不要解释"
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except:
        return "（摘要失败）"

def get_image(entry):
    try:
        if "media_content" in entry:
            return entry.media_content[0]["url"]
        if "links" in entry:
            for link in entry.links:
                if link.type.startswith("image"):
                    return link.href
    except:
        pass
    return None

def get_source(url):
    if "bbc" in url:
        return "BBC"
    if "cnn" in url:
        return "CNN"
    if "nytimes" in url:
        return "NYT"
    if "reuters" in url:
        return "Reuters"
    if "guardian" in url:
        return "Guardian"
    if "time" in url:
        return "TIME"
    return "News"

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

                    summary = ai_summary(entry.title)
                    image = get_image(entry)
                    source = get_source(link)
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")

                    message = f"""📰 全球要闻

{summary}

来源：{source}
时间：{now}
"""

                    if image:
                        send_photo(message, image)
                    else:
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            data={"chat_id": CHAT_ID, "text": message}
                        )

                    print("✅ 发送:", summary)

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(600)  # 10分钟

if __name__ == "__main__":
    run()
