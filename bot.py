from flask import Flask
import requests
import os
import feedparser
import time
import threading

TOKEN = "8233133696:AAErhEUJdRf3MGib6FRJO2tHAMvLDipkqto"
CHAT_ID = "7502932042"

app = Flask(__name__)

last_news = ""

# 重大新闻关键词
KEYWORDS = [
"war","attack","strike","missile","military",
"president","election","government","policy",
"economy","inflation","bank","market","fed",
"AI","technology","chip","Tesla","Apple",
"China","Russia","USA","NATO","EU","UN"
]

def translate(text):

    url = "https://translate.googleapis.com/translate_a/single"

    params = {
        "client":"gtx",
        "sl":"auto",
        "tl":"zh",
        "dt":"t",
        "q":text
    }

    r = requests.get(url,params=params)

    return r.json()[0][0][0]


def is_major_news(title):

    title = title.lower()

    for k in KEYWORDS:

        if k in title:
            return True

    return False


def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url,json={
        "chat_id":CHAT_ID,
        "text":text
    })


def format_news(entry):

    title = entry.title
    link = entry.link
    desc = entry.summary

    chinese = translate(desc)

    message = f"""
🌍 全球重大新闻

📰 {title}

📌 事件摘要
{chinese}

🔗 原文
{link}
"""

    return message


def news_loop():

    global last_news

    while True:

        feed = feedparser.parse(
        "https://rss.cnn.com/rss/edition.rss"
        )

        for entry in feed.entries[:5]:

            if entry.link != last_news:

                if is_major_news(entry.title):

                    msg = format_news(entry)

                    send_message(msg)

                    last_news = entry.link

                    break

        time.sleep(300)


@app.route("/")
def home():
    return "News bot running"


if __name__ == "__main__":

    thread = threading.Thread(target=news_loop)

    thread.start()

    port = int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)
