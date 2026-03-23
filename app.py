import feedparser, requests, time, os, json
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

sent = set()

RSS_LIST = [
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.vogue.com/feed/rss"
]

def send(text, img):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
        data={"chat_id": CHAT_ID, "caption": text, "photo": img}
    )

def main():
    print("🔥 Professional News Bot Running")

    while True:
        print("📰 scanning...")

        for rss in RSS_LIST:
            feed = feedparser.parse(rss)

            for entry in feed.entries[:3]:
                if entry.link in sent:
                    continue

                sent.add(entry.link)

                send("测试新闻：" + entry.title, "")

        time.sleep(300)

if __name__ == "__main__":
    main()
