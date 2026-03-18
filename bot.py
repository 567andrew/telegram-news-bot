from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re
from bs4 import BeautifulSoup

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

app = Flask(__name__)

posted=set()

NEWS_FEEDS={

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
"CNBC":"https://www.cnbc.com/id/100727362/device/rss/rss.html",
"TechCrunch":"https://techcrunch.com/feed/",
"Forbes":"https://www.forbes.com/world-news/feed/"
}

# 自动翻译
def translate(text):

    try:

        url="https://translate.googleapis.com/translate_a/single"

        params={
            "client":"gtx",
            "sl":"auto",
            "tl":"zh",
            "dt":"t",
            "q":text[:1000]
        }

        r=requests.get(url,params=params,timeout=10)

        return r.json()[0][0][0]

    except:

        return text


# 抓取新闻正文
def fetch_article(url):

    try:

        r=requests.get(url,timeout=10)

        soup=BeautifulSoup(r.text,"lxml")

        paragraphs=soup.find_all("p")

        text=" ".join([p.get_text() for p in paragraphs[:5]])

        return text

    except:

        return ""


# 提取图片
def extract_image(summary):

    if not summary:
        return None

    img=re.search(r'<img.*?src="(.*?)"',summary)

    if img:
        return img.group(1)

    return None


# 提取视频
def extract_video(summary):

    if not summary:
        return None

    video=re.search(r'<video.*?src="(.*?)"',summary)

    if video:
        return video.group(1)

    return None


# 新闻分类
def classify_news(text):

    text=text.lower()

    if any(word in text for word in ["israel","iran","gaza","middle east","hormuz"]):
        return "⚠️ MIDDLE EAST"

    if any(word in text for word in ["war","missile","attack","military"]):
        return "⚔️ WAR"

    if any(word in text for word in ["economy","inflation","bank","market"]):
        return "💰 ECONOMY"

    if any(word in text for word in ["ai","technology","chip","robot"]):
        return "🧠 TECH"

    return "🌍 WORLD"


# 构建新闻内容
def build_intel(entry,source):

    text=entry.title

    article=fetch_article(entry.link)

    if article:
        text=entry.title+" "+article

    chinese=translate(text)

    category=classify_news(text)

    message=f"""
🌍 GLOBAL INTEL

{category}

{chinese}

SOURCE
{source}
"""

    return message


# 发送文字
def send_message(text):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url,json={
        "chat_id":CHAT_ID,
        "text":text
    })


# 发送图片
def send_photo(photo,text):

    try:

        url=f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        requests.post(
            url,
            data={
                "chat_id":CHAT_ID,
                "caption":text
            },
            files={
                "photo":requests.get(photo,timeout=10).content
            }
        )

    except:

        send_message(text)


# 发送视频
def send_video(video,text):

    try:

        url=f"https://api.telegram.org/bot{TOKEN}/sendVideo"

        requests.post(
            url,
            data={
                "chat_id":CHAT_ID,
                "caption":text
            },
            files={
                "video":requests.get(video,timeout=20).content
            }
        )

    except:

        send_message(text)


# 新闻扫描
def news_loop():

    print("GLOBAL INTEL RADAR STARTED")

    while True:

        try:

            for source,url in NEWS_FEEDS.items():

                print("Scanning:",source)

                feed=feedparser.parse(url)

                if not feed.entries:
                    continue

                for entry in feed.entries[:3]:

                    if entry.link in posted:
                        continue

                    intel=build_intel(entry,source)

                    img=None
                    video=None

                    if hasattr(entry,"summary"):

                        img=extract_image(entry.summary)
                        video=extract_video(entry.summary)

                    if img:

                        send_photo(img,intel)

                    elif video:

                        send_video(video,intel)

                    else:

                        send_message(intel)

                    posted.add(entry.link)

                    time.sleep(2)

        except Exception as e:

            print("ERROR:",e)

        print("Next scan in 60 seconds")

        time.sleep(60)


@app.route("/")
def home():

    return "Global Intel Radar Running"


@app.route("/test")
def test():

    send_message("新闻机器人测试成功")

    return "Test OK"


if __name__=="__main__":

    print("GLOBAL INTEL SYSTEM STARTED")

    send_message("全球情报雷达系统启动")

    thread=threading.Thread(target=news_loop)
    thread.daemon=True
    thread.start()

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)
