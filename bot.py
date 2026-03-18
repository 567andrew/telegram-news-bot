from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re
from bs4 import BeautifulSoup
from datetime import datetime

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

# HTML清理
def clean_html(text):

    soup=BeautifulSoup(text,"lxml")

    return soup.get_text()


# 清理垃圾文本
def clean_article(text):

    bad_words=[
        "enable javascript",
        "disable ad blocker",
        "advertisement",
        "sign up"
    ]

    for w in bad_words:

        text=text.replace(w,"")

    return text


# 翻译
def translate(text):

    try:

        url="https://translate.googleapis.com/translate_a/single"

        params={
            "client":"gtx",
            "sl":"auto",
            "tl":"zh",
            "dt":"t",
            "q":text[:1200]
        }

        r=requests.get(url,params=params,timeout=10)

        return r.json()[0][0][0]

    except:

        return text


# 抓取正文
def fetch_article(url):

    try:

        r=requests.get(url,timeout=10)

        soup=BeautifulSoup(r.text,"lxml")

        paragraphs=soup.select("article p")

        if not paragraphs:
            paragraphs=soup.select("main p")

        if not paragraphs:
            paragraphs=soup.find_all("p")

        text=" ".join([p.get_text() for p in paragraphs[:6]])

        return clean_article(text)

    except:

        return ""


# 分类
def classify_news(text):

    text=text.lower()

    if any(w in text for w in ["israel","iran","gaza","hormuz","middle east"]):
        return "MIDDLE EAST"

    if any(w in text for w in ["war","attack","missile","airstrike","bomb"]):
        return "WAR"

    if any(w in text for w in ["economy","inflation","bank","market"]):
        return "ECONOMY"

    if any(w in text for w in ["ai","technology","chip","robot"]):
        return "TECH"

    return "WORLD"


# 日期
def news_time():

    now=datetime.utcnow()

    return now.strftime("%d %b")


# 图片提取
def extract_image(entry):

    try:

        if "media_content" in entry:

            for m in entry.media_content:

                if "url" in m:

                    return m["url"]

        if hasattr(entry,"summary"):

            img=re.search(r'<img.*?src="(.*?)"',entry.summary)

            if img:

                return img.group(1)

        r=requests.get(entry.link,timeout=10)

        soup=BeautifulSoup(r.text,"lxml")

        tag=soup.find("meta",property="og:image")

        if tag:

            return tag["content"]

    except:

        pass

    return None


# 构建新闻
def build_intel(entry,source):

    text=entry.title

    if hasattr(entry,"summary"):
        text=entry.title+" "+entry.summary

    article=fetch_article(entry.link)

    if article:
        text=text+" "+article

    text=clean_html(text)

    chinese=translate(text)

    category=classify_news(text)

    date=news_time()

    message=f"""🌍 GLOBAL INTEL
▸ {category}

{chinese}

SOURCE
{source} | {date}
"""

    return message


# 发送消息
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
                "photo":requests.get(photo,timeout=15).content
            }
        )

    except:

        send_message(text)


# 新闻循环
def news_loop():

    print("GLOBAL INTEL RADAR STARTED")

    while True:

        try:

            for source,url in NEWS_FEEDS.items():

                feed=feedparser.parse(url)

                if not feed.entries:
                    continue

                for entry in feed.entries[:3]:

                    if entry.link in posted:
                        continue

                    intel=build_intel(entry,source)

                    img=extract_image(entry)

                    if img:
                        send_photo(img,intel)
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
