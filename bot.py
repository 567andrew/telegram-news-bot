import feedparser
import requests
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "@world_monitor_news"

RSS_FEEDS = [
"https://feeds.bbci.co.uk/news/world/rss.xml",
"https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
"https://www.aljazeera.com/xml/rss/all.xml"
]

sent_links = set()

def send_message(text):
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
            link = entry.link

            message = f"""🌍 World Monitor

{title}

{link}
"""

            send_message(message)

            sent_links.add(link)

def main():
    while True:
        fetch_news()
        time.sleep(300)

main()
