import requests
import feedparser

TOKEN = "8233133696:AAErhEUJdRf3MGib6FRJO2tHAMvLDipkqto"
CHAT_ID = "7502932042"

feeds = {
    "CNN": "https://rss.cnn.com/rss/edition.rss",
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "AP": "https://rsshub.app/apnews/topics/apf-topnews"
}

def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })


def fetch_news():

    for source, url in feeds.items():

        feed = feedparser.parse(url)

        if len(feed.entries) == 0:
            continue

        for entry in feed.entries[:2]:

            message = f"""
🌍 {source}

{entry.title}

{entry.link}
"""

            send_message(message)


if __name__ == "__main__":

    fetch_news()
