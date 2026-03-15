import requests
import time
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "-100你的频道ID"

NEWS_API = "https://api.rss2json.com/v1/api.json?rss_url=https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

def get_news():
    r = requests.get(NEWS_API)
    data = r.json()
    return data["items"][:3]

sent = set()

while True:
    try:
        news = get_news()

        for n in news:
            title = n["title"]
            link = n["link"]

            if link not in sent:
                msg = f"{title}\n{link}"
                send_message(msg)
                sent.add(link)

        time.sleep(300)

    except Exception as e:
        print(e)
        time.sleep(60)
