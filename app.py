import feedparser, requests, time, os

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )
    print(r.text)  # 👈 打印结果

def main():
    print("🔥 Bot Running")

    while True:
        print("📰 scanning...")

        feed = feedparser.parse("https://rss.cnn.com/rss/edition.rss")

        for entry in feed.entries[:3]:
            send("测试：" + entry.title)

        time.sleep(60)

if __name__ == "__main__":
    main()
