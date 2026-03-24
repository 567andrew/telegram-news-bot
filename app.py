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

# ✅ 全球主流媒体
RSS_LIST = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    "https://time.com/feed/",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://apnews.com/rss",
    "https://www.bloomberg.com/feed/podcast/etf-report.xml"
]

sent_links = set()
sent_titles = []

# ✅ 提取图片
def extract_image(entry):
    if "media_content" in entry:
        return entry.media_content[0]["url"]

    if "summary" in entry:
        imgs = re.findall(r'<img.*?src="(.*?)"', entry.summary)
        if imgs:
            return imgs[0]

    return None

# ✅ 简单去重（标题相似）
def is_similar(title):
    for t in sent_titles:
        if title[:20] in t or t[:20] in title:
            return True
    return False

def send_photo(text, image_url):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "photo": image_url,
            "caption": text
        })
    except:
        pass

def ai_summary(text):
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "提取新闻核心（谁做了什么、发生了什么、结果），一句话中文总结（30-50字）"
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
    if "bbc" in url: return "BBC"
    if "cnn" in url: return "CNN"
    if "nytimes" in url: return "NYT"
    if "reuters" in url: return "REUTERS"
    if "guardian" in url: return "GUARDIAN"
    if "time" in url: return "TIME"
    if "apnews" in url: return "AP"
    if "aljazeera" in url: return "AJ"
    if "bloomberg" in url: return "BLOOMBERG"
    return "NEWS"

def run():
    print("🚀 新闻系统启动")

    while True:
        try:
            for rss in RSS_LIST:
                feed = feedparser.parse(rss)

                for entry in feed.entries[:5]:
                    link = entry.link
                    title = entry.title

                    # ✅ 去重
                    if link in sent_links:
                        continue
                    if is_similar(title):
                        continue

                    # ✅ 必须有图
                    image = extract_image(entry)
                    if not image:
                        continue

                    content = title + " " + entry.get("summary", "")
                    summary = ai_summary(content)

                    if not summary:
                        continue

                    sent_links.add(link)
                    sent_titles.append(title)

                    source = get_source(link)
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")

                    message = f"""{summary}

{source} {now}"""

                    send_photo(message, image)

                    print("✅ 已发送:", summary)

                    time.sleep(5)  # 防封

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(600)

if __name__ == "__main__":
    run()
