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
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

app = Flask(__name__)
posted = set()

# 🔥 状态控制
FIRST_RUN = True
AI_LIMIT_PER_ROUND = 3

# ================== 新闻源 ==================
NEWS_FEEDS = [
    ("Reuters","https://www.reutersagency.com/feed/?best-topics=world&post_type=best"),
    ("BBC","http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("CNN","https://rss.cnn.com/rss/edition.rss"),
    ("Guardian","https://www.theguardian.com/world/rss"),
    ("NYTimes","https://rss.nytimes.com/services/xml/rss/nyt/World.xml")
]

# ================== 工具 ==================

def clean_html(text):
    soup = BeautifulSoup(text, "lxml")
    return soup.get_text()

def fetch_full_article(url):
    try:
        r = requests.get(url, timeout=8)
        soup = BeautifulSoup(r.text, "lxml")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        return re.sub(r'\s+', ' ', text)[:4000]
    except:
        return ""

# ================== AI ==================

def ai_process(text):
    if not client:
        return None

    prompt = f"""
提取新闻要点：

时间：
地点：
人物：
事件：
原因：
结果：

一句话总结：

新闻：
{text[:2500]}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return res.choices[0].message.content.strip()
    except:
        return None

# ================== fallback ==================

def translate(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "zh",
            "dt": "t",
            "q": text[:500]
        }
        r = requests.get(url, params=params, timeout=5)
        return r.json()[0][0][0]
    except:
        return text

def fallback_summary(text):
    return f"【新闻快讯】\n\n{translate(text[:120])}"

# ================== 去重 ==================

def is_duplicate(title):
    key = title.lower()
    if key in posted:
        return True
    posted.add(key)
    return False

# ================== 发送 ==================

def send_photo(photo, text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": text},
            files={"photo": requests.get(photo, timeout=5).content},
            timeout=10
        )
    except:
        pass

# ================== 单条处理 ==================

def process_news(entry, source, ai_count):

    if is_duplicate(entry.title):
        return ai_count

    raw = getattr(entry, "summary", "")
    full = fetch_full_article(entry.link)

    text = full if len(full) > 300 else raw
    text = clean_html(text)

    if len(text) < 100:
        return ai_count

    # 🔥 AI控制
    use_ai = (not FIRST_RUN) and ai_count < AI_LIMIT_PER_ROUND

    if use_ai:
        result = ai_process(text)
        ai_count += 1
    else:
        result = None

    if not result:
        result = fallback_summary(text)

    date = datetime.now(UTC).strftime("%d %b").lower()

    final_text = f"{result}\n\n———\n🌍 {source} · {date}"

    img = f"https://source.unsplash.com/800x600/?news"

    send_photo(img, final_text)

    return ai_count

# ================== 主循环 ==================

def news_loop():
    global FIRST_RUN

    print("🔥 NEWS LOOP STARTED")

    index = 0

    while True:

        ai_count = 0

        # 🔥 每轮只处理2个新闻源（关键优化）
        batch = NEWS_FEEDS[index:index+2]

        for source, url in batch:
            try:
                feed = feedparser.parse(url)

                for entry in feed.entries[:2]:
                    ai_count = process_news(entry, source, ai_count)
                    time.sleep(1)

            except:
                continue

        index = (index + 2) % len(NEWS_FEEDS)

        FIRST_RUN = False

        time.sleep(120)  # 🔥 扫描间隔

# ================== Web ==================

@app.route("/", methods=["GET"])
def home():
    return "OK"

# ================== 启动 ==================

def start_news():
    time.sleep(5)  # 🔥 延迟启动
    news_loop()

if __name__ == "__main__":

    print("🔥 SYSTEM STARTED")

    t = threading.Thread(target=start_news)
    t.daemon = True
    t.start()

    print("🔥 NEWS THREAD STARTED")

    app.run(host="0.0.0.0", port=10000)
