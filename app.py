import time
import requests
import os
import feedparser
from openai import OpenAI

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

sent_links = set()

def send_photo(text, image_url):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "caption": text,
        "photo": image_url
    })

def get_news():
    urls = [
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    ]

    all_news = []
    for url in urls:
        feed = feedparser.parse(url)
        all_news.extend(feed.entries[:3])

    return all_news

def ai_summary(text):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "总结新闻，输出3句话，简单清晰"},
                {"role": "user", "content": text}
            ]
        )
        return res.choices[0].message.content
    except:
        return "（AI总结失败）"

def main():
    print("🔥 Bot started")

    while True:
        try:
            print("📡 checking news...")

            news_list = get_news()

            for news in news_list:
                link = news.link
                title = news.title
                summary = news.get("summary", "")

                if link in sent_links:
                    continue

                print("👉 处理:", title)

                ai_text = ai_summary(title + "\n" + summary)

                # 尝试找图片
                image_url = ""
                if "media_content" in news:
                    image_url = news.media_content[0]["url"]

                text = f"""📰 {title}

🤖 AI总结：
{ai_text}

🔗 阅读原文：
{link}
"""

                if image_url:
                    send_photo(text, image_url)
                else:
                    # 没图就普通发送
                    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

                sent_links.add(link)

                print("✅ 已发送")
                time.sleep(5)

            time.sleep(120)

        except Exception as e:
            print("❌ error:", e)
            time.sleep(10)

if __name__ == "__main__":
    main()
