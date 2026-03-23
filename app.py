import requests
import os
import feedparser
import time
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# 发送消息
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

# 抓新闻（BBC）
def get_news():
    feed = feedparser.parse("http://feeds.bbci.co.uk/news/rss.xml")
    news_list = []
    
    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link
        news_list.append(f"{title}\n{link}")
    
    return news_list

# 自动循环
def run_bot():
    sent = set()

    while True:
        news_list = get_news()

        for news in news_list:
            if news not in sent:
                send_message(news)
                sent.add(news)
                time.sleep(5)

        time.sleep(600)  # 每10分钟检查一次


# Flask测试
@app.route("/")
def home():
    return "Bot is running!"

@app.route("/test")
def test():
    send_message("测试成功！自动新闻系统已启动")
    return "OK"


# 启动
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
