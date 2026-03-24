import requests
import feedparser
import time
import os
from openai import OpenAI

# ========= 环境变量 =========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

print("🔥 程序启动")
print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)

if not BOT_TOKEN or not CHAT_ID or not OPENAI_API_KEY:
    print("❌ 环境变量缺失")
    exit()

client = OpenAI(api_key=OPENAI_API_KEY, timeout=20)

RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"

# ========= 去重 =========
SEEN_FILE = "seen.txt"

def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(f.read().splitlines())
    except:
        return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(seen))

# ========= Telegram =========
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data, timeout=10)

# ========= 获取新闻 =========
def get_feed():
    print("📡 获取新闻中...")
    r = requests.get(RSS_URL, timeout=10)
    return feedparser.parse(r.content)

# ========= AI处理 =========
def process_news(title, summary):
    content = (title + "\n" + summary)[:2000]

    prompt = f"""
请处理这条新闻：

1. 用中文总结（100字以内）
2. 生成标题
3. 提取3个关键词

内容：
{content}

格式：
标题：
总结：
关键词：
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content

# ========= 主程序 =========
def run():
    print("🚀 机器人开始运行")

    seen = load_seen()

    while True:
        try:
            feed = get_feed()

            for entry in feed.entries[:5]:
                if entry.link in seen:
                    continue

                print("📰 新新闻:", entry.title)

                ai_result = process_news(entry.title, entry.summary)

                message = f"""
<b>{entry.title}</b>

{ai_result}

<a href="{entry.link}">查看原文</a>
"""

                send_telegram(message)

                print("✅ 已发送")

                seen.add(entry.link)
                save_seen(seen)

                time.sleep(5)

        except Exception as e:
            print("❌ 错误:", e)

        print("⏳ 等待下一轮...")
        time.sleep(60)

# ========= 启动 =========
if __name__ == "__main__":
    print("🚀 程序启动成功")
    run()
