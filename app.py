import requests
import feedparser
import time
import os
import re
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

# ✅ 提取图片
def extract_image(entry):
    # 优先 media_content
    if "media_content" in entry:
        return entry.media_content[0]["url"]

    # 从 summary 里找 img
    if "summary" in entry:
        imgs = re.findall(r'<img.*?src="(.*?)"', entry.summary)
        if imgs:
            return imgs[0]

    return None

def send_photo(text, image_url):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "photo": image_url,
            "caption": text
        })
    except:
        # 如果图片发送失败 → fallback成文字
        send_message(text)

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
                    "content": "提取新闻核心（谁做了什么、发生了什么、结果），用一句中文表达（30-50字）"
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

                    content = entry.title + " " + entry.get("summary", "")
                    summary = ai_summary(content)

                    if not summary:
                        continue

                    image = extract_image(entry)

                    source = get_source(link)
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")

                    message = f"""{summary}

{source} {now}"""

                    # ✅ 有图发图，没有发文字
                    if image:
                        send_photo(message, image)
                    else:
                        send_message(message)

                    print("✅ 已发送:", summary)

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(600)

if __name__ == "__main__":
    run()
