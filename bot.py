from flask import Flask
import requests
import os
import feedparser
import time

TOKEN = "8233133696:AAErhEUJdRf3MGib6FRJO2tHAMvLDipkqto"
CHAT_ID = "7502932042"

app = Flask(__name__)

last_news = ""

def translate(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": "zh",
        "dt": "t",
        "q": text
    }
    r = requests.get(url, params=params)
    result = r.json()
    return result[0][0][0]


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })


def format_news(entry):

    title = entry.title
    link = entry.link
    description = entry.summary

    chinese = translate(description)

    message = f"""
🌍 CNN

📰 {title}

📌 新闻摘要
{chinese}

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

🔗 {link}
"""

    return message


def news_loop():

    global last_news

    while True:

        feed = feedparser.parse(
            "https://rss.cnn.com/rss/edition.rss"
        )

        entry = feed.entries[0]

        if entry.link != last_news:

            message = format_news(entry)

            send_message(message)

            last_news = entry.link

        time.sleep(300)


@app.route("/")
def home():
    return "News bot running"


if __name__ == "__main__":

    import threading

    thread = threading.Thread(target=news_loop)
    thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
