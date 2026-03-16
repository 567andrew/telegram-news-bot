from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re

TOKEN="你的BOT_TOKEN"
CHAT_ID="-1003800156451"

app=Flask(__name__)

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
"Forbes":"https://www.forbes.com/world-news/feed/"
}

def send_message(text):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    r=requests.post(url,json={
        "chat_id":CHAT_ID,
        "text":text
    })

    print("Telegram:",r.text)


def send_photo(photo,text):

    try:

        url=f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        r=requests.post(url,
            data={
                "chat_id":CHAT_ID,
                "caption":text
            },
            files={
                "photo":requests.get(photo,timeout=5).content
            }
        )

        print("Photo:",r.text)

    except:

        send_message(text)


def extract_image(summary):

    img=re.search(r'<img.*?src="(.*?)"',summary)

    if img:
        return img.group(1)

    return None


def build_news(entry,source):

    title=entry.title

    message=f"""
🌍 全球新闻

标题
{title}

WHO
Unknown

WHAT
{title}

WHERE
Global

WHEN
Latest

WHY
Developing

SRC
{source}
"""

    return message


def news_loop():

    print("GLOBAL RADAR STARTED")

    while True:

        try:

            for source,url in NEWS_FEEDS.items():

                print("Scanning:",source)

                feed=feedparser.parse(url)

                for entry in feed.entries[:10]:

                    if entry.link not in posted:

                        msg=build_news(entry,source)

                        img=extract_image(entry.summary)

                        if img:
                            send_photo(img,msg)
                        else:
                            send_message(msg)

                        posted.add(entry.link)

                        break

                time.sleep(1)

        except Exception as e:

            print("ERROR:",e)

        time.sleep(300)


@app.route("/")
def home():

    return "Global Radar Running"


@app.route("/test")
def test():

    send_message("Radar Test OK")

    return "Test OK"


if __name__=="__main__":

    print("SUPER GLOBAL RADAR STARTED")

    send_message("全球雷达系统启动")

    thread=threading.Thread(target=news_loop)
    thread.daemon=True
    thread.start()

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)
