import feedparser
import requests
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "@world_monitor_news"

RSS_FEEDS = [
"https://feeds.bbci.co.uk/news/world/rss.xml",
"https://www.aljazeera.com/xml/rss/all.xml"
]

sent_links = set()

def send_message(text):

    if not BOT_TOKEN:
        print("BOT_TOKEN not set")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url, data=data)

def fetch_news():

    for feed in RSS_FEEDS:

        parsed = feedparser.parse(feed)

        for entry in parsed.entries[:3]:

            if entry.link in sent_links:
                continue

            title = entry.title

            message = f"🌍 World Monitor\n\n{title}\n\n{entry.link}"

            send_message(message)

            sent_links.add(entry.link)

def main():

    print("Bot started")

    while True:

        try:
            fetch_news()
        except Exception as e:
            print(e)

        time.sleep(300)

main()
