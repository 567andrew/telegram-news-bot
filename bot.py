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

# ================== 新闻源 ==================
NEWS_FEEDS = {
    "Reuters":"https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    "BBC":"http://feeds.bbci.co.uk/news/world/rss.xml",
    "CNN":"https://rss.cnn.com/rss/edition.rss",
    "Guardian":"https://www.theguardian.com/world/rss",
    "NYTimes":"https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
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
        text = " ".join([p.get_text() for p in paragraphs])

        text = re.sub(r'\s+', ' ', text)

        return text[:5000]
    except:
        return ""

# ================== AI ==================

def ai_process(text):

    if not client:
        return None

    prompt = f"""
你是国际新闻编辑，请基于新闻正文提取完整信息：

【新闻摘要】

时间：
地点：
人物：
事件：
原因：
结果：

一句话总结：

【要求】
- 只根据正文内容
- 不参考标题
- 不编造
- 简单清晰
- 每条不超过20字

新闻正文：
{text[:3000]}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        output = res.choices[0].message.content.strip()

        if not output or "事件：" not in output:
            return None

        return output

    except Exception as e:
        print("AI错误:", e)
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
            "q": text[:1200]
        }
        r = requests.get(url, params=params, timeout=10)
        return r.json()[0][0][0]
    except:
        return text

def fallback_summary(text):
    short = translate(text[:120])
    return f"""【新闻快讯】

{short}

（正文摘要）"""

# ================== 去重 ==================

def is_duplicate(title):
    key = title.lower()
    if key in posted:
        return True
    posted.add(key)
    if len(posted) > 1000:
        posted.clear()
    return False

# ================== 图片 ==================

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

def fallback_image(text):
    keyword = text.split()[0]
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
    except Exception as e:
        print("发送失败:", e)

# ================== 核心 ==================

def process_news(entry, source):

    try:
        if is_duplicate(entry.title):
            return

        print("📰 处理:", entry.title)

        # 🔥 不用标题，只用正文
        raw = getattr(entry, "summary", "")
        full = fetch_full_article(entry.link)

        text = full if len(full) > 300 else raw
        text = clean_html(text)
        text = re.sub(r'\s+', ' ', text)

        if len(text) < 100:
            print("⚠️ 正文太短跳过")
            return

        # 🔥 AI判断（只对重要新闻）
        important = any(k in text.lower() for k in [
            "war","attack","china","us","trump",
            "russia","iran","israel","election"
        ])

        if important:
            result = ai_process(text)
        else:
            result = None

        if not result:
            result = fallback_summary(text)

        date = datetime.now(UTC).strftime("%d %b").lower()

        final_text = f"""{result}

———
🌍 {source} · {date}
"""

        img = extract_image(entry)
        if not img:
            img = fallback_image(text)

        send_photo(img, final_text)

        print("✅ 已发送")

    except Exception as e:
        print("❌ 处理失败:", e)

# ================== 主循环 ==================

def news_loop():

    print("🔥 NEWS LOOP STARTED")

    while True:
        for source, url in NEWS_FEEDS.items():
            try:
                feed = feedparser.parse(url)

                count = 0

                for entry in feed.entries:

                    if count >= 2:  # 限制数量，防卡
                        break

                    process_news(entry, source)
                    count += 1

                    time.sleep(2)

                time.sleep(2)

            except Exception as e:
                print("ERROR:", e)

        time.sleep(180)

# ================== Web ==================

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "HEAD"])
@app.route("/<path:path>", methods=["GET", "POST", "HEAD"])
def catch_all(path):
    return "OK"

# ================== 启动 ==================

def start_news():
    while True:
        try:
            news_loop()
        except Exception as e:
            print("线程崩溃:", e)
            time.sleep(5)

if __name__ == "__main__":

    print("🔥 SYSTEM STARTED")

    t = threading.Thread(target=start_news)
    t.daemon = True
    t.start()

    print("🔥 NEWS THREAD STARTED")

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
