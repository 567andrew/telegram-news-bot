from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re
from bs4 import BeautifulSoup
from datetime import datetime, UTC
from openai import OpenAI

# ================== 配置 ==================
TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

posted = set()

NEWS_FEEDS = {
    "Reuters":"https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    "BBC":"http://feeds.bbci.co.uk/news/world/rss.xml",
    "CNN":"https://rss.cnn.com/rss/edition.rss",
    "AP":"https://apnews.com/rss",
    "Guardian":"https://www.theguardian.com/world/rss",
    "NYTimes":"https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "Bloomberg":"https://feeds.bloomberg.com/world/news.rss",
    "AlJazeera":"https://www.aljazeera.com/xml/rss/all.xml",
    "DW":"https://rss.dw.com/xml/rss-en-world",
    "France24":"https://www.france24.com/en/rss",
    "CNBC":"https://www.cnbc.com/id/100727362/device/rss/rss.html"
}

# ================== 工具 ==================

def clean_html(text):
    soup = BeautifulSoup(text, "lxml")
    return soup.get_text()

def fetch_full_article(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        paragraphs = soup.find_all("p")
        return " ".join([p.get_text() for p in paragraphs])[:3000]
    except:
        return ""

# ✅ AI总结
def ai_process(text):

    prompt = f"""
提取新闻要素，用中文输出：

必须包含：
- 发生了什么
- 谁
- 地点
- 时间（如果有）
- 结果

至少3条要点，不要废话。

如果不是新闻或信息不足，返回：INVALID

{text[:2000]}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        output = res.choices[0].message.content.strip()

        if "INVALID" in output:
            return None

        return output

    except:
        return None

# 翻译备用
def translate(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "zh",
            "dt": "t",
            "q": text[:1200]
        }
        r = requests.get(url, params=params, timeout=10)
        return r.json()[0][0][0]
    except:
        return text

# 去重
def is_duplicate(title):
    key = title.lower()
    if key in posted:
        return True
    posted.add(key)
    if len(posted) > 1000:
        posted.clear()
    return False

# 图片
def extract_image(entry):
    try:
        if "media_content" in entry:
            return entry.media_content[0]["url"]

        if hasattr(entry, "summary"):
            img = re.search(r'<img.*?src="(.*?)"', entry.summary)
            if img:
                return img.group(1)
    except:
        pass
    return None

def fallback_image(title):
    keyword = title.split()[0]
    return f"https://source.unsplash.com/800x600/?{keyword}"

# ================== 发送 ==================

def send_photo(photo, text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": text},
            files={"photo": requests.get(photo, timeout=10).content},
            timeout=15
        )
    except:
        pass  # 失败直接放弃

# ================== 核心 ==================

def process_news(entry, source):

    if is_duplicate(entry.title):
        return

    print("📰 处理:", entry.title)

    raw = entry.title + " " + getattr(entry, "summary", "")

    full = fetch_full_article(entry.link)
    text = full if len(full) > 200 else raw

    text = clean_html(text)

    result = ai_process(text)

    # ❗AI失败 fallback（保证一定发送）
    if not result:
        result = translate(text[:500])

    date = datetime.now(UTC).strftime("%d %b").lower()

    final_text = f"{result}\n\n_{source.lower()} · {date}_"

    img = extract_image(entry)
    if not img:
        img = fallback_image(entry.title)

    send_photo(img, final_text)

# ================== 主循环 ==================

def news_loop():

    print("🔥 NEWS LOOP STARTED")

    while True:
        for source, url in NEWS_FEEDS.items():
            try:
                feed = feedparser.parse(url)

                for entry in feed.entries:
                    process_news(entry, source)
                    time.sleep(1)

            except Exception as e:
                print("ERROR:", e)

        time.sleep(60)

# ================== Web ==================

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "HEAD"])
@app.route("/<path:path>", methods=["GET", "POST", "HEAD"])
def catch_all(path):
    return "OK"

# ================== 启动 ==================

if __name__ == "__main__":

    # Flask 放子线程
    threading.Thread(
        target=app.run,
        kwargs={
            "host": "0.0.0.0",
            "port": int(os.environ.get("PORT", 10000))
        },
        daemon=True
    ).start()

    # 主线程跑新闻（关键）
    news_loop()
