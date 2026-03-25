import requests
import feedparser
import time
import os
import re
from datetime import datetime
from openai import OpenAI
from pytrends.request import TrendReq

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# 🌍 15家媒体
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
    "https://www.ft.com/rss/home",
    "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "https://www.forbes.com/real-time/feed2/",
    "https://www.newsweek.com/rss",
    "https://www.economist.com/latest/rss.xml"
]

# 🖼️ 提取图片
def extract_image(entry):
    if "media_content" in entry:
        return entry.media_content[0]["url"]

    if "summary" in entry:
        imgs = re.findall(r'<img.*?src="(.*?)"', entry.summary)
        if imgs:
            return imgs[0]

    return None

# 🌐 AI补图
def search_image(query):
    return f"https://source.unsplash.com/800x600/?{query}"

# 🧠 AI新闻快讯
def ai_summary(text):
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是专业新闻编辑，请写一条新闻快讯："
                        "必须包含【地点+人物+事件+结果】，"
                        "翻译为中文，一句话30-60字，不要解释"
                    )
                },
                {
                    "role": "user",
                    "content": text[:1200]
                }
            ]
        )
        return response.choices[0].message.content.strip()[:80]
    except:
        return None

# 📤 发送
def send_photo(text, image_url):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={"chat_id": CHAT_ID, "photo": image_url, "caption": text}
    )

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )

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
    if "ft.com" in url: return "FT"
    if "cnbc" in url: return "CNBC"
    if "forbes" in url: return "FORBES"
    if "newsweek" in url: return "NEWSWEEK"
    if "economist" in url: return "ECONOMIST"
    return "NEWS"

# 🔥 全球趋势
def get_trending_topics():
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        df = pytrends.trending_searches(pn='worldwide')
        return df[0].tolist()[:15]
    except:
        return []

# 🔥 AI热点榜
def build_hot_list(trends, news_titles):
    try:
        text = "趋势:\n" + "\n".join(trends)
        text += "\n\n新闻:\n" + "\n".join(news_titles[:20])

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "整理全球最重要的10个热点，"
                        "合并重复，每条一句中文（20-40字），按重要性排序"
                    )
                },
                {
                    "role": "user",
                    "content": text[:2000]
                }
            ]
        )

        return response.choices[0].message.content.strip()
    except:
        return None

# 🕗 定时
last_hot_day = ""

def check_hot_time():
    global last_hot_day
    now = datetime.now()
    if now.strftime("%H") == "20" and last_hot_day != now.strftime("%Y-%m-%d"):
        last_hot_day = now.strftime("%Y-%m-%d")
        return True
    return False

# 🚀 主程序
def run():
    print("🚀 全球新闻系统启动")

    while True:
        sent = set()
        news_titles = []

        try:
            # 🔥 热点榜
            if check_hot_time():
                trends = get_trending_topics()
                hot = build_hot_list(trends, news_titles)
                if hot:
                    send_message(f"🌍 今日全球热点 Top10\n\n{hot}")
                    print("🔥 热点已发送")

            for rss in RSS_LIST:
                feed = feedparser.parse(rss)

                for entry in feed.entries[:5]:
                    link = entry.link
                    title = entry.title

                    if link in sent:
                        continue

                    news_titles.append(title)

                    content = title + " " + entry.get("summary", "")
                    summary = ai_summary(content)

                    if not summary or len(summary) < 20:
                        continue

                    image = extract_image(entry)
                    if not image:
                        image = search_image(title)

                    source = get_source(link)
                    date = datetime.now().strftime("%Y-%m-%d")

                    message = f"{summary}\n\n{source} {date}"

                    send_photo(message, image)

                    sent.add(link)

                    print("✅ 已发送:", summary)

                    time.sleep(5)

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(600)


if __name__ == "__main__":
    run()
