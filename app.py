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
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://apnews.com/rss",
]

sent_links = set()
sent_titles = []

# 🖼️ 提取图片（增强版）
def extract_image(entry):
    if "media_content" in entry:
        return entry.media_content[0]["url"]

    if "summary" in entry:
        imgs = re.findall(r'<img.*?src="(.*?)"', entry.summary)
        if imgs:
            return imgs[0]

    return None

# 🔁 去重（最近20条）
def is_similar(title):
    for t in sent_titles[-20:]:
        if title[:15] in t or t[:15] in title:
            return True
    return False

# 📤 发图
def send_photo(text, image_url):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "photo": image_url,
            "caption": text
        })
    except:
        send_message(text)

# 📤 发文字
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# 🧠 AI快讯（核心）
def ai_summary(text):
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是专业新闻编辑，请写一条新闻快讯："
                        "格式必须为：【国家】+一句完整新闻句子，"
                        "内容包含人物、事件和结果，"
                        "30-60字，语言自然像媒体报道，不要解释"
                    )
                },
                {
                    "role": "user",
                    "content": text[:1200]
                }
            ]
        )

        result = response.choices[0].message.content.strip()

        # ❌ 去AI痕迹
        bad = ["谁", "什么", "总结", "分析", "AI", "："]
        for b in bad:
            if b in result[:10]:
                return None

        return result[:80]

    except:
        return None

# 🏷️ 来源
def get_source(url):
    if "bbc" in url: return "BBC"
    if "cnn" in url: return "CNN"
    if "nytimes" in url: return "NYT"
    if "reuters" in url: return "REUTERS"
    if "guardian" in url: return "GUARDIAN"
    if "time" in url: return "TIME"
    if "apnews" in url: return "AP"
    if "aljazeera" in url: return "AJ"
    return "NEWS"

# 🚀 主程序
def run():
    print("🚀 专业新闻系统启动")

    while True:
        try:
            for rss in RSS_LIST:
                feed = feedparser.parse(rss)

                for entry in feed.entries[:5]:
                    link = entry.link
                    title = entry.title

                    if link in sent_links:
                        continue
                    if is_similar(title):
                        continue

                    content = title + " " + entry.get("summary", "")
                    summary = ai_summary(content)

                    if not summary or len(summary) < 20:
                        continue

                    image = extract_image(entry)

                    sent_links.add(link)
                    sent_titles.append(title)

                    source = get_source(link)
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")

                    message = f"""{summary}

{source} {now}"""

                    if image:
                        send_photo(message, image)
                    else:
                        send_message(message)

                    print("✅ 已发送:", summary)

                    time.sleep(5)

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(600)

if __name__ == "__main__":
    run()
