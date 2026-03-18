from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re
from bs4 import BeautifulSoup
from datetime import datetime, UTC

TOKEN=os.environ["BOT_TOKEN"]
CHAT_ID=os.environ["CHAT_ID"]

app=Flask(__name__)

posted=set()
posted_titles=set()

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

# ------------------------
# 工具函数
# ------------------------

def clean_html(text):
    soup=BeautifulSoup(text,"lxml")
    return soup.get_text()

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


def fetch_article(url):

    try:

        r=requests.get(url,timeout=10)

        soup=BeautifulSoup(r.text,"lxml")

        paragraphs=soup.find_all("p")

        text=" ".join([p.get_text() for p in paragraphs[:6]])

        return text

    except:

        return ""


# ------------------------
# AI摘要
# ------------------------

def ai_summary(text):

    sentences=re.split(r'[。.!?]',text)

    clean=[s.strip() for s in sentences if len(s.strip())>15]

    if len(clean)>=4:
        return clean[0]+"。"+clean[1]+"。"+clean[2]+"。"+clean[3]+"。"

    if len(clean)>=3:
        return clean[0]+"。"+clean[1]+"。"+clean[2]+"。"

    return text


# ------------------------
# 新闻分段
# ------------------------

def format_text(text):

    sentences=re.split(r'[。.!?]',text)

    clean=[s.strip() for s in sentences if len(s.strip())>10]

    if len(clean)>=4:
        return clean[0]+"。\n\n"+clean[1]+"。 "+clean[2]+"。 "+clean[3]+"。"

    return text


# ------------------------
# 分类
# ------------------------

def classify_news(text):

    text=text.lower()

    if any(w in text for w in ["war","missile","attack","airstrike"]):
        return "war"

    if any(w in text for w in ["economy","bank","inflation","market"]):
        return "economy"

    if any(w in text for w in ["ai","chip","robot","technology"]):
        return "tech"

    return "world"


# ------------------------
# 去重
# ------------------------

def normalize_title(title):

    title=title.lower()

    title=re.sub(r'[^a-z0-9 ]','',title)

    words=title.split()

    return " ".join(words[:6])


# ------------------------
# 时间
# ------------------------

def news_time():

    now=datetime.now(UTC)

    return now.strftime("%d %b").lower()


# ------------------------
# 图片提取
# ------------------------

def extract_image(entry):

    try:

        if "media_content" in entry:

            for m in entry.media_content:

                if "url" in m:

                    return m["url"]

        if "media_thumbnail" in entry:

            for m in entry.media_thumbnail:

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


# ------------------------
# 视频提取
# ------------------------

def extract_video(entry):

    try:

        if hasattr(entry,"summary"):

            video=re.search(r'<video.*?src="(.*?)"',entry.summary)

            if video:

                return video.group(1)

    except:

        pass

    return None


# ------------------------
# 构建新闻
# ------------------------

def build_intel(entry,source):

    text=entry.title

    if hasattr(entry,"summary"):

        text=entry.title+" "+entry.summary

    article=fetch_article(entry.link)

    if article:

        text=text+" "+article

    text=clean_html(text)

    chinese=translate(text)

    chinese=ai_summary(chinese)

    chinese=format_text(chinese)

    category=classify_news(text)

    date=news_time()

    message=f"""🌍 GLOBAL INTEL
▸ {category}

{chinese}

source
{source.lower()} | {date}
"""

    return message


# ------------------------
# Telegram发送
# ------------------------

def send_message(text):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url,json={"chat_id":CHAT_ID,"text":text})


def send_photo(photo,text):

    try:

        url=f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        requests.post(

            url,

            data={"chat_id":CHAT_ID,"caption":text},

            files={"photo":requests.get(photo,timeout=15).content}

        )

    except:

        send_message(text)


def send_video(video,text):

    try:

        url=f"https://api.telegram.org/bot{TOKEN}/sendVideo"

        requests.post(

            url,

            data={"chat_id":CHAT_ID,"caption":text},

            files={"video":requests.get(video,timeout=20).content}

        )

    except:

        send_message(text)


# ------------------------
# 新闻循环
# ------------------------

def news_loop():

    print("GLOBAL INTEL RADAR STARTED")

    while True:

        try:

            for source,url in NEWS_FEEDS.items():

                feed=feedparser.parse(url)

                if not feed.entries:
                    continue

                for entry in feed.entries[:3]:

                    key=(entry.title+entry.link).lower()

                    title_key=normalize_title(entry.title)

                    if key in posted or title_key in posted_titles:

                        continue

                    intel=build_intel(entry,source)

                    img=extract_image(entry)

                    video=extract_video(entry)

                    if img:

                        send_photo(img,intel)

                    elif video:

                        send_video(video,intel)

                    else:

                        send_message(intel)

                    posted.add(key)
                    posted_titles.add(title_key)

                    if len(posted)>500:
                        posted.clear()

                    if len(posted_titles)>500:
                        posted_titles.clear()

                    time.sleep(2)

        except Exception as e:

            print("ERROR:",e)

        time.sleep(300)


# ------------------------
# X trending
# ------------------------

def fetch_x_trending():

    try:

        url="https://nitter.net/explore"

        r=requests.get(url,timeout=10)

        soup=BeautifulSoup(r.text,"lxml")

        tweets=soup.select(".timeline-item")

        titles=[]

        for t in tweets[:10]:

            text=t.get_text()

            text=re.sub(r'\s+',' ',text)

            titles.append(text[:120])

        return titles

    except:

        return []


def x_daily_loop():

    sent_today=False

    while True:

        now=datetime.now()

        if now.hour==11 and now.minute==55 and not sent_today:

            tweets=fetch_x_trending()

            if tweets:

                text="🌍 GLOBAL INTEL\n▸ social\n\nx trending today\n\n"

                for i,t in enumerate(tweets,1):

                    text+=f"{i}. {t}\n"

                text+="\nsource\nx | trending"

                send_message(text)

            sent_today=True

        if now.hour==0:

            sent_today=False

        time.sleep(60)


# ------------------------
# Flask
# ------------------------

@app.route("/",methods=["GET","POST"])
def home():

    return "Global Intel Radar Running"


@app.route("/test",methods=["GET","POST"])
def test():

    send_message("新闻机器人测试成功")

    return "Test OK"


# ------------------------
# MAIN
# ------------------------

if __name__=="__main__":

    print("GLOBAL INTEL SYSTEM STARTED")

    send_message("全球情报雷达系统启动")

    thread=threading.Thread(target=news_loop)

    thread.daemon=True

    thread.start()

    xthread=threading.Thread(target=x_daily_loop)

    xthread.daemon=True

    xthread.start()

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)
