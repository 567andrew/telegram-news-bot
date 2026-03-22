from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re
from bs4 import BeautifulSoup
from datetime import datetime, UTC

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

app = Flask(__name__)

posted = set()
posted_titles = []

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

# 清理HTML
def clean_html(text):
    soup = BeautifulSoup(text, "lxml")
    return soup.get_text()

# 翻译
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

# 新闻过滤（核心）
def is_valid_news(text):

    text_lower = text.lower()

    # ❌ 问句
    if "?" in text:
        return False

    # ❌ 分析/观点类
    bad_words = ["opinion", "analysis", "why", "how", "should"]
    if any(w in text_lower for w in bad_words):
        return False

    # ✅ 必须有事件
    event_words = [
        "killed", "attack", "attacked", "launched",
        "announced", "arrested", "strike", "explosion",
        "war", "clash", "fire", "crash"
    ]

    if not any(w in text_lower for w in event_words):
        return False

    return True

# 抓全文
def fetch_full_article(url):

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])

        return text[:3000]

    except:
        return ""

# 摘要优化
def ai_summary(text):

    sentences = re.split(r'[。.!?]', text)

    selected = []
    for s in sentences:
        s = s.strip()
        if len(s) > 15:
            selected.append(s)

    if len(selected) >= 5:
        selected = selected[:5]

    return "\n".join([f"• {s}" for s in selected])

# 去重
def similar(title):

    words = set(title.lower().split())

    for old in posted_titles:
        if len(words & old) >= 4:
            return True

    posted_titles.append(words)
    return False

# 提取图片
def extract_image(entry):

    try:
        if "media_content" in entry:
            for m in entry.media_content:
                if "url" in m:
                    return m["url"]

        if hasattr(entry, "summary"):
            img = re.search(r'<img.*?src="(.*?)"', entry.summary)
            if img:
                return img.group(1)

    except:
        pass

    return None

# fallback图片（保证一定有图）
def fallback_image(title):

    keyword = title.split()[0]
    return f"https://source.unsplash.com/800x600/?{keyword}"

# 构建内容（核心升级）
def build_intel(entry, source):

    raw_text = entry.title + " " + getattr(entry, "summary", "")

    # ❗过滤垃圾新闻
    if not is_valid_news(raw_text):
        return None

    # 抓全文
    full_text = fetch_full_article(entry.link)

    if len(full_text) > 200:
        text = full_text
    else:
        text = raw_text

    text = clean_html(text)

    chinese = translate(text)

    chinese = ai_summary(chinese)

    date = datetime.now(UTC).strftime("%d %b").lower()

    return f"""{chinese}

_{source.lower()} · {date}_"""

# 发送文字
def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

# 发送图片
def send_photo(photo, text):

    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": text
            },
            files={
                "photo": requests.get(photo, timeout=15).content
            }
        )

    except:
        send_message(text)

# 主循环
def news_loop():

    print("GLOBAL INTEL STARTED")

    while True:

        try:

            for source, url in NEWS_FEEDS.items():

                feed = feedparser.parse(url)

                if not feed.entries:
                    continue

                for entry in feed.entries[:6]:

                    key = entry.title + entry.link

                    if key in posted:
                        continue

                    if similar(entry.title):
                        continue

                    intel = build_intel(entry, source)

                    # ❗过滤后为空
                    if not intel:
                        continue

                    img = extract_image(entry)

                    if not img:
                        img = fallback_image(entry.title)

                    send_photo(img, intel)

                    posted.add(key)

                    if len(posted) > 500:
                        posted.clear()

                    time.sleep(2)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(300)

@app.route("/")
def home():
    return "Running"

@app.route("/test")
def test():
    send_message("系统正常运行")
    return "OK"

if __name__ == "__main__":

    print("SYSTEM STARTED")

    thread = threading.Thread(target=news_loop)
    thread.daemon = True
    thread.start()

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
