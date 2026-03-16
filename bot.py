from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re

TOKEN = "你的BOT_TOKEN"
CHAT_ID = "你的CHAT_ID"

app = Flask(__name__)

posted_news=set()

NEWS_FEEDS={

"Reuters":"https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
"AP":"https://apnews.com/rss",
"BBC":"http://feeds.bbci.co.uk/news/world/rss.xml",
"CNN":"https://rss.cnn.com/rss/edition.rss",
"Guardian":"https://www.theguardian.com/world/rss",

"NYTimes":"https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
"AlJazeera":"https://www.aljazeera.com/xml/rss/all.xml",
"FoxNews":"http://feeds.foxnews.com/foxnews/world",
"Bloomberg":"https://feeds.bloomberg.com/world/news.rss",
"CNBC":"https://www.cnbc.com/id/100727362/device/rss/rss.html",

"CBS":"https://www.cbsnews.com/latest/rss/world",
"ABC":"https://abcnews.go.com/abcnews/internationalheadlines",

"France24":"https://www.france24.com/en/rss",
"DW":"https://rss.dw.com/xml/rss-en-world",
"SkyNews":"https://feeds.skynews.com/feeds/rss/world.xml"
}

def translate(text):

    try:

        url="https://translate.googleapis.com/translate_a/single"

        params={
            "client":"gtx",
            "sl":"auto",
            "tl":"zh",
            "dt":"t",
            "q":text[:500]
        }

        r=requests.get(url,params=params,timeout=5)

        return r.json()[0][0][0]

    except:

        return text


def news_score(text):

    text=text.lower()

    score=0

    important=[
    "war","attack","missile","military","conflict",
    "china","russia","usa","iran","israel",
    "president","government","election"
    ]

    medium=[
    "economy","bank","oil","gas",
    "technology","ai","cyber"
    ]

    normal=[
    "police","crime","flood","storm",
    "earthquake","explosion","disaster"
    ]

    for w in important:
        if w in text:
            score+=3

    for w in medium:
        if w in text:
            score+=2

    for w in normal:
        if w in text:
            score+=1

    return score


def extract_image(summary):

    img=re.search(r'<img.*?src="(.*?)"',summary)

    if img:
        return img.group(1)

    return None


def send_message(text):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url,json={
        "chat_id":CHAT_ID,
        "text":text
    })


def send_photo(photo,text):

    try:

        url=f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        requests.post(url,data={
            "chat_id":CHAT_ID,
            "caption":text
        },files={
            "photo":requests.get(photo,timeout=5).content
        })

    except:

        send_message(text)


def format_news(entry,source):

    title=entry.title
    summary=entry.summary

    chinese=translate(summary)

    short=chinese[:120]

    message=f"""
🌍 全球新闻

📰 {title}

📌 摘要
{chinese}

🧾 总结
{short}

👤 Who
Unknown

📍 Where
Unknown

⏰ When
Recent

⚡ What
{title}

❓ Why
Developing

📰 来源：{source}
"""

    return message


def news_loop():

    global posted_news

    print("NEWS BOT STARTED")

    while True:

        try:

            for source,url in NEWS_FEEDS.items():

                print("Scanning",source)

                feed=feedparser.parse(url)

                for entry in feed.entries[:40]:

                    if entry.link not in posted_news:

                        text=entry.title+entry.summary

                        score=news_score(text)

                        if score>=2:

                            print("News found:",entry.title)

                            msg=format_news(entry,source)

                            img=extract_image(entry.summary)

                            if img:

                                send_photo(img,msg)

                            else:

                                send_message(msg)

                            posted_news.add(entry.link)

                            if len(posted_news)>1000:
                                posted_news.clear()

                            break

                time.sleep(1)

        except Exception as e:

            print("ERROR:",e)

        time.sleep(300)


@app.route("/")
def home():

    return "Global News Radar Running"


@app.route("/test")
def test():

    send_message("雷达机器人测试成功 ✅")

    return "Test OK"


if __name__=="__main__":

    print("Starting Radar Bot...")

    thread=threading.Thread(target=news_loop)

    thread.daemon=True

    thread.start()

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)
