from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re

TOKEN="你的BOT_TOKEN"
CHAT_ID="@world_monitor_news"

app=Flask(__name__)

posted_news=set()

NEWS_FEEDS={

"Reuters":"https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
"AP":"https://apnews.com/rss",
"BBC":"http://feeds.bbci.co.uk/news/world/rss.xml",
"CNN":"https://rss.cnn.com/rss/edition.rss",
"Guardian":"https://www.theguardian.com/world/rss",

"NYTimes":"https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
"Bloomberg":"https://feeds.bloomberg.com/world/news.rss",
"AlJazeera":"https://www.aljazeera.com/xml/rss/all.xml",
"FoxNews":"http://feeds.foxnews.com/foxnews/world",
"CNBC":"https://www.cnbc.com/id/100727362/device/rss/rss.html",

"CBS":"https://www.cbsnews.com/latest/rss/world",
"ABC":"https://abcnews.go.com/abcnews/internationalheadlines",
"SkyNews":"https://feeds.skynews.com/feeds/rss/world.xml",
"DW":"https://rss.dw.com/xml/rss-en-world",
"France24":"https://www.france24.com/en/rss",

"Politico":"https://www.politico.com/rss/politics08.xml",
"Axios":"https://api.axios.com/feed/",
"Time":"https://time.com/feed/",
"Forbes":"https://www.forbes.com/world-news/feed/"
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

📰 来源：{source}
"""

    return message


def news_loop():

    global posted_news

    print("NEWS RADAR STARTED")

    while True:

        try:

            for source,url in NEWS_FEEDS.items():

                print("Scanning",source)

                feed=feedparser.parse(url)

                for entry in feed.entries[:40]:

                    if entry.link not in posted_news:

                        text=entry.title+entry.summary

                        msg=format_news(entry,source)

                        img=extract_image(entry.summary)

                        if img:
                            send_photo(img,msg)
                        else:
                            send_message(msg)

                        posted_news.add(entry.link)

                        if len(posted_news)>2000:
                            posted_news.clear()

                        break

                time.sleep(1)

        except Exception as e:

            print("ERROR:",e)

        time.sleep(120)


@app.route("/")
def home():

    return "Global News Radar Running"


@app.route("/test")
def test():

    send_message("机器人运行正常 ✅")

    return "Test OK"


if __name__=="__main__":

    print("Starting Global News Radar")

    thread=threading.Thread(target=news_loop)

    thread.daemon=True

    thread.start()

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)
