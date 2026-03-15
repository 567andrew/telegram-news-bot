import feedparser
import requests
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "@world_monitor_news"

def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url, data=data)

def main():

    send_message("🌍 World Monitor Bot started")

    feed = feedparser.parse("https://feeds.bbci.co.uk/news/world/rss.xml")

    for entry in feed.entries[:5]:

        title = entry.title
        link = entry.link

        msg = f"🌍 World Monitor\n\n{title}\n\n{link}"

        send_message(msg)

    while True:
        time.sleep(600)

main()
