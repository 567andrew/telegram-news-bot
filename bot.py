from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re

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
            "q":text[:500]
        }

        r=requests.get(url,params=params,timeout=5)

        return r.json()[0][0][0]

    except:

        return text


def send_message(text):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url,json={
        "chat_id":CHAT_ID,
        "text":text
    })


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
                "photo":requests.get(photo,timeout=5).content
            }
        )

    except:

        send_message(text)


def extract_image(summary):

    img=re.search(r'<img.*?src="(.*?)"',summary)

    if img:
        return img.group(1)

    return None


# 情报模板生成
def build_intel(entry,source):

    text = entry.title

    if hasattr(entry,"summary"):
        text = entry.title + ". " + entry.summary

    chinese = translate(text)

    intel = chinese[:160]

    message=f"""
🌍 GLOBAL INTEL

{intel}

SRC
{source}
"""

    return message


def news_loop():

    print("GLOBAL INTEL RADAR STARTED")

    while True:

        try:

            for source,url in NEWS_FEEDS.items():

                print("Scanning:",source)

                feed=feedparser.parse(url)

                if not feed.entries:
                    continue

                entry=feed.entries[0]

                if entry.link not in posted:

                    intel=build_intel(entry,source)

                    img=None

                    if hasattr(entry,"summary"):
                        img=extract_image(entry.summary)

                    if img:
                        send_photo(img,intel)
                    else:
                        send_message(intel)

                    posted.add(entry.link)

                time.sleep(1)

        except Exception as e:

            print("ERROR:",e)

        print("Next scan in 5 minutes")

        time.sleep(300)


@app.route("/")
def home():
    return "Global Intel Radar Running"


@app.route("/test")
def test():
    send_message("情报系统测试成功")
    return "Test OK"


if __name__=="__main__":

    print("GLOBAL INTEL SYSTEM STARTED")

    send_message("全球情报雷达系统启动")

    thread=threading.Thread(target=news_loop)
    thread.daemon=True
    thread.start()

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)
