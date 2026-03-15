import requests
import feedparser

TOKEN = "8233133696:AAErhEUJdRf3MGib6FRJO2tHAMvLDipkqto"
CHAT_ID = "7502932042"

RSS_URL = "https://rss.cnn.com/rss/edition.rss"

def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

    print("Telegram response:", response.text)


def fetch_news():

    print("Fetching CNN news...")

    feed = feedparser.parse(RSS_URL)

    if len(feed.entries) == 0:
        send_message("TEST: RSS working but no news")
        return

    entry = feed.entries[0]

    message = f"""
🌍 CNN NEWS TEST

{entry.title}

{entry.link}
"""

    send_message(message)


if __name__ == "__main__":

    fetch_news()
