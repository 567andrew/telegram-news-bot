from flask import Flask
import requests
import os
import feedparser
import time
import threading
import re

TOKEN = "你的TOKEN"
CHAT_ID = "你的CHATID"

app = Flask(__name__)

last_news = ""

NEWS_FEEDS = {
"CNN":"https://rss.cnn.com/rss/edition.rss",
"BBC":"http://feeds.bbci.co.uk/news/world/rss.xml",
"Reuters":"https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
"AP":"https://apnews.com/rss",
"Guardian":"https://www.theguardian.com/world/rss"
}

KEYWORDS = [
"war","attack","missile","military","conflict",
"president","election","government",
"china","russia","usa","nato","iran",
"economy","inflation","bank","oil","gas",
"ai","technology","cyber"
]

def translate(text):

    url="https://translate.googleapis.com/translate_a/single"

    params={
    "client":"gtx",
    "sl":"auto",
    "tl":"zh",
    "dt":"t",
    "q":text
    }

    r=requests.get(url,params=params)

    return r.json()[0][0][0]


def is_major_news(title):

    title=title.lower()

    for k in KEYWORDS:

        if k in title:
            return True

    return False


def extract_image(summary):

    img = re.search(r'<img.*?src="(.*?)"',summary)

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

    url=f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    requests.post(url,data={
    "chat_id":CHAT_ID,
    "caption":text
    },files={
    "photo":requests.get(photo).content
    })


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

📰 来源
{source}
"""

    return message


def news_loop():

    global last_news

    while True:

        for source,url in NEWS_FEEDS.items():

            feed=feedparser.parse(url)

            for entry in feed.entries[:12]:

                if entry.link!=last_news:

                    if is_major_news(entry.title):

                        msg=format_news(entry,source)

                        img=extract_image(entry.summary)

                        if img:

                            send_photo(img,msg)

                        else:

                            send_message(msg)

                        last_news=entry.link

                        break

        time.sleep(300)


@app.route("/")
def home():
    return "News bot running"


if __name__=="__main__":

    thread=threading.Thread(target=news_loop)

    thread.start()

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)
