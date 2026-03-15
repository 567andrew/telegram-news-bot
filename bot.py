from flask import Flask
import requests
import feedparser
import html
import threading
import time

TOKEN = "你的TOKEN"
CHAT_ID = "7502932042"

feeds = {
    "CNN": "https://rss.cnn.com/rss/edition.rss",
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "REUTERS": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best"
}

sent_links = set()

app = Flask(__name__)


def translate(text):

    url = "https://translate.googleapis.com/translate_a/single"

    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": "zh-CN",
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


def clean_title(title):

    title = html.unescape(title)

    if " - " in title:
        title = title.split(" - ")[0]

    return title


def fetch_news():

    for source, url in feeds.items():

        feed = feedparser.parse(url)

        if len(feed.entries) == 0:
            continue

        for entry in feed.entries:

            if entry.link in sent_links:
                continue

            sent_links.add(entry.link)

            title = clean_title(entry.title)

            chinese = translate(title)

            message = f"""
🌍 {source}

📰 {title}

📖 {chinese}

🔗 {entry.link}
"""

            send_message(message)

            break


def news_loop():

    while True:

        print("Checking news...")

        fetch_news()

        time.sleep(300)


@app.route("/", methods=["GET","POST"])
def home():
    return "News bot running"


if __name__ == "__main__":

    thread = threading.Thread(target=news_loop)
    thread.start()

    app.run(host="0.0.0.0", port=10000)
