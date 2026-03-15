import feedparser
import requests
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "@world_monitor_news"

RSS_FEEDS = [
"https://feeds.reuters.com/reuters/worldNews",
"https://feeds.reuters.com/reuters/topNews",
"https://www.aljazeera.com/xml/rss/all.xml",
"https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
"https://feeds.bbci.co.uk/news/world/rss.xml"
]

sent_links = set()

def translate_text(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": "zh-CN",
        "dt": "t",
        "q": text
    }
    r = requests.get(url, params=params)
    return r.json()[0][0][0]

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def fetch_news():
    for feed in RSS_FEEDS:
        parsed = feedparser.parse(feed)

        for entry in parsed.entries[:5]:

            if entry.link in sent_links:
                continue

            title = entry.title
            link = entry.link

            try:
                zh_title = translate_text(title)
            except:
                zh_title = title

            message = f"""🌍 World Monitor

{zh_title}

Source: {feed}
Link: {link}
"""

            send_message(message)

            sent_links.add(link)

def main():
    while True:
        fetch_news()
        time.sleep(300)

main()
