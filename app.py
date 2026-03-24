import time

print("🔥 程序启动成功")

while True:
    print("✅ 循环正在运行")
    time.sleep(10)import time
import requests
import os
import feedparser
from openai import OpenAI

# ================== 配置 ==================
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

sent_links = set()

# ================== 发送 ==================
def send_photo(text, image_url):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "caption": text[:1000],  # Telegram限制
        "photo": image_url
    })

def send_text(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text[:4000]
    })

# ================== 获取新闻 ==================
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

# ================== AI处理 ==================
def ai_process(title, summary):
    text = f"{title}\n{summary}"

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "你是新闻助手，请输出：1.中文总结（3句话）2.英文翻译 3.新闻要素（人物、事件、地点、原因）"
                },
                {
                    "role": "user",
                    "content": text[:1000]
                }
            ]
        )
        return res.choices[0].message.content.strip()

    except Exception as e:
        print("❌ AI错误:", e)
        return "（AI处理失败）"

# ================== 图片提取 ==================
def get_image(news):
    if "media_content" in news:
        return news.media_content[0]["url"]

    if "links" in news:
        for link in news.links:
            if "image" in link.get("type", ""):
                return link.href

    return ""

# ================== 主程序 ==================
def main():
    print("🔥 Bot started")

    while True:
        try:
            print("📡 checking news...")

            news_list = get_news()

            for news in news_list:
                title = news.title
                link = news.link
                summary = news.get("summary", "")

                if link in sent_links:
                    continue

                print("👉 处理:", title)

                ai_text = ai_process(title, summary)

                image_url = get_image(news)

                final_text = f"""📰 {title}

🤖 AI内容：
{ai_text}

🔗 阅读原文：
{link}
"""

                if image_url:
                    send_photo(final_text, image_url)
                else:
                    send_text(final_text)

                print("✅ 已发送")

                sent_links.add(link)

                time.sleep(5)

            time.sleep(60)

        except Exception as e:
            print("❌ 主循环错误:", e)
            time.sleep(10)

if __name__ == "__main__":
    main()
