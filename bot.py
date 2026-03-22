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

# AI压缩（保留信息，不乱删）
def ai_summary(text):

    sentences = re.split(r'[。.!?]', text)

    clean = []
    for s in sentences:
        s = s.strip()
        if len(s) > 10:
            clean.append(s)

    # 保留最多5句（保证信息完整）
    if len(clean) >= 5:
        selected = clean[:5]
    elif len(clean) >= 3:
        selected = clean
    else:
        return text

    return "\n".join([f"• {s}" for s in selected])

# 去重优化
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

# 构建内容（核心）
def build_intel(entry, source):

    text = entry.title

    if hasattr(entry, "summary"):
        text += " " + entry.summary

    text = clean_html(text)

    chinese = translate(text)

    chinese = ai_summary(chinese)

    date = datetime.now(UTC).strftime("%d %b").lower()

    return f"""{chinese}

_ {source.lower()} · {date}
"""

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

                    img = extract_image(entry)

                    if img:
                        send_photo(img, intel)
                    else:
                        send_message(intel)

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
