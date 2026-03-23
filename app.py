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

def ai_process(text):
    prompt = f"（放上面的prompt）\n\n{text}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    content = res.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return None

def main():
    print("🔥 Professional News Bot Started")

    while True:
        for rss in RSS_LIST:
            feed = feedparser.parse(rss)

            for entry in feed.entries[:5]:
                if entry.link in sent:
                    continue

                text = entry.title + entry.summary

                data = ai_process(text)

                if not data:
                    continue

                if (
                    not data["translation"]
                    or not data["summary"]
                    or data["score"] < 6
                ):
                    continue

                img = entry.get("media_content", [{}])[0].get("url", "")

                if not img:
                    continue

                sent.add(entry.link)

                msg = f"""
📰【全球快报】

📍 {data['where']}
👤 {data['who']}
📌 {data['what']}
📊 {data['impact']}

🧠 解读：
{data['summary']}

📖 翻译：
{data['translation']}
"""

                send(msg, img)

        time.sleep(300)

if __name__ == "__main__":
    main()
