import requests
import os
import feedparser
import time
import threading
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ================== 发送消息 ==================
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        res = requests.post(url, data=data)
        print("发送结果:", res.text)
    except Exception as e:
        print("发送失败:", e)


# ================== 获取新闻 ==================
def get_news():
    feed = feedparser.parse("http://feeds.bbci.co.uk/news/rss.xml")
    news_list = []

    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link
        news = f"📰 {title}\n{link}"
        news_list.append(news)

    return news_list


# ================== 自动运行 ==================
def run_bot():
    print("🚀 自动新闻系统启动...")

    sent_news = set()

    while True:
        try:
            news_list = get_news()

            for news in news_list:
                if news not in sent_news:
                    send_message(news)
                    sent_news.add(news)
                    time.sleep(3)

            print("⏳ 等待30秒...")
            time.sleep(30)   # 🔥 测试用（30秒）

        except Exception as e:
            print("错误:", e)
            time.sleep(10)


# ================== 测试接口 ==================
@app.route("/")
def home():
    return "Bot is running!"

@app.route("/test")
def test():
    send_message("✅ 测试成功！自动新闻系统运行中")
    return "OK"


# ================== 启动 ==================
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
