from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re
from bs4 import BeautifulSoup
from datetime import datetime,UTC

TOKEN=os.environ["BOT_TOKEN"]
CHAT_ID=os.environ["CHAT_ID"]

app=Flask(__name__)

posted=set()
posted_titles=[]

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
"Forbes":"https://www.forbes.com/world-news/feed/",
"FinancialTimes":"https://www.ft.com/?format=rss",
"Economist":"https://www.economist.com/international/rss.xml",
"WashingtonPost":"https://feeds.washingtonpost.com/rss/world",
"FoxNews":"http://feeds.foxnews.com/foxnews/world",
"SkyNews":"https://feeds.skynews.com/feeds/rss/world.xml",
"ABC":"https://abcnews.go.com/abcnews/internationalheadlines",
"CBS":"https://www.cbsnews.com/latest/rss/world",
"NBC":"https://feeds.nbcnews.com/nbcnews/public/world",
"NPR":"https://feeds.npr.org/1004/rss.xml",
"Politico":"https://www.politico.com/rss/politics08.xml",
"Axios":"https://api.axios.com/feed/",
"Time":"https://time.com/feed/",
"Newsweek":"https://www.newsweek.com/rss",
"SCMP":"https://www.scmp.com/rss/91/feed",
"JapanTimes":"https://www.japantimes.co.jp/feed/",
"NHK":"https://www3.nhk.or.jp/rss/news/cat0.xml",
"KoreaHerald":"http://www.koreaherald.com/common_prog/rssdisp.php?ct=020000000000.xml",
"HindustanTimes":"https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml",
"StraitsTimes":"https://www.straitstimes.com/news/world/rss.xml",
"Australian":"https://www.theaustralian.com.au/world/rss",
"RT":"https://www.rt.com/rss/news/",
"TASS":"https://tass.com/rss/v2.xml"
}

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

def ai_summary(text):

    sentences=re.split(r'[。.!?]',text)

    clean=[s.strip() for s in sentences if len(s.strip())>15]

    if len(clean)>=4:
        return clean[0]+"。"+clean[1]+"。"+clean[2]+"。"+clean[3]+"。"

    return text

def format_text(text):

    sentences=re.split(r'[。.!?]',text)

    clean=[s.strip() for s in sentences if len(s.strip())>10]

    if len(clean)>=3:
        return clean[0]+"。\n\n"+clean[1]+"。 "+clean[2]+"。"

    return text

def classify_news(text):

    text=text.lower()

    if any(w in text for w in ["war","missile","attack","airstrike"]):
        return "war"

    if any(w in text for w in ["economy","bank","inflation","market"]):
        return "economy"

    if any(w in text for w in ["ai","chip","robot","technology"]):
        return "tech"

    return "world"

def similar(title):

    words=set(title.lower().split())

    for old in posted_titles:

        if len(words & old)>=3:
            return True

    posted_titles.append(words)

    return False

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

    except:
        pass

    return None

def build_intel(entry,source):

    text=entry.title

    if hasattr(entry,"summary"):
        text=text+" "+entry.summary

    text=clean_html(text)

    chinese=translate(text)

    chinese=ai_summary(chinese)

    chinese=format_text(chinese)

    category=classify_news(text)

    date=datetime.now(UTC).strftime("%d %b").lower()

    return f"""🌍 GLOBAL INTEL
▸ {category}

{chinese}

source
{source.lower()} | {date}
"""

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

def news_loop():

    print("GLOBAL INTEL RADAR STARTED")

    while True:

        try:

            for source,url in NEWS_FEEDS.items():

                feed=feedparser.parse(url)

                if not feed.entries:
                    continue

                for entry in feed.entries[:8]:

                    key=(entry.title+entry.link)

                    if key in posted:
                        continue

                    if similar(entry.title):
                        continue

                    intel=build_intel(entry,source)

                    img=extract_image(entry)

                    if img:
                        send_photo(img,intel)
                    else:
                        send_message(intel)

                    posted.add(key)

                    if len(posted)>800:
                        posted.clear()

                    time.sleep(1)

        except Exception as e:
            print("ERROR:",e)

        time.sleep(300)

@app.route("/",methods=["GET","POST"])
def home():
    return "Global Intel Radar Running"

@app.route("/test",methods=["GET","POST"])
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
