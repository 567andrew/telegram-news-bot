import feedparser
import requests
import time
import os
import json
from openai import OpenAI

# ====== API配置 ======
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ====== 已发送去重 ======
sent = set()

# ====== 新闻源 ======
RSS_LIST = [
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.vogue.com/feed/rss"
]

# ====== 发送消息 ======
def send(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )
    print("发送结果：", r.text)

# ====== AI处理 ======
def ai_process(text):
    prompt = f"""
你是专业新闻编辑，请完成：

1. 翻译成中文
2. 提取核心信息（谁 / 做了什么 / 影响）
3. 写一句简短总结（50字内）

输出格式：

【翻译】
xxx

【要点】
xxx

【总结】
xxx

新闻：
{text}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        print("AI错误：", e)
        return None

# ====== 主程序 ======
def main():
    print("🔥 Professional News Bot Running")

    while True:
        print("📰 正在扫描新闻...")

        for rss in RSS_LIST:
            try:
                feed = feedparser.parse(rss)

                for entry in feed.entries[:5]:

                    if entry.link in sent:
                        continue

                    sent.add(entry.link)

                    content = entry.title + "\n" + entry.summary

                    print("👉 处理新闻：", entry.title)

                    result = ai_process(content)

                    if not result:
                        continue

                    msg = f"""
📰【全球快报】

{result}
"""

                    send(msg)

                    # 防止频率过高
                    time.sleep(3)

            except Exception as e:
                print("RSS错误：", e)

        print("⏳ 等待5分钟...\n")
        time.sleep(300)

# ====== 启动 ======
if __name__ == "__main__":
    main()
