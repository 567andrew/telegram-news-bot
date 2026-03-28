import time
import requests
import feedparser
import json
import os
from openai import OpenAI

# ========= 配置 =========
TELEGRAM_TOKEN = "你的token"
CHAT_ID = "你的chat_id"
OPENAI_API_KEY = "你的key"

RSS_LIST = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "http://feeds.bbci.co.uk/news/world/rss.xml"
]

client = OpenAI(api_key=OPENAI_API_KEY)

# ========= 去重文件 =========
HISTORY_FILE = "sent_news.json"

def load_sent():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent), f)

sent_titles = load_sent()

# ========= 发送消息 =========
def send_telegram(text, image=None):
    print("📤 发送中...")

    try:
        if image:
            res = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "caption": text,
                    "parse_mode": "Markdown"
                },
                files={"photo": requests.get(image).content}
            )
        else:
            res = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": text,
                    "parse_mode": "Markdown"
                }
            )

        print("✅ 发送成功", res.status_code)

    except Exception as e:
        print("❌ 发送失败:", e)


# ========= AI分析 =========
def analyze_news(title, summary):
    print("🤖 AI分析中...")

    prompt = f"""
你是一个国际顶级智库分析师（类似兰德公司）。

请分析：

标题: {title}
内容: {summary}

输出：
1. 中文翻译
2. 核心事件
3. 深度分析
4. 影响评估
5. 趋势判断

要求：简洁、专业、像情报报告
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"AI分析失败: {e}"


# ========= 抓新闻 =========
def fetch_news():
    print("🌍 抓取新闻中...")

    results = []

    for rss in RSS_LIST:
        feed = feedparser.parse(rss)

        for entry in feed.entries[:5]:
            image = None

            if "media_content" in entry:
                image = entry.media_content[0].get("url")

            results.append({
                "title": entry.title,
                "summary": entry.summary if "summary" in entry else "",
                "link": entry.link,
                "image": image
            })

    print(f"📰 抓到 {len(results)} 条新闻")
    return results


# ========= 主流程 =========
def run():
    global sent_titles

    news_list = fetch_news()

    for news in news_list:
        title = news["title"]

        if title in sent_titles:
            print("⏭ 已发送过，跳过:", title)
            continue

        print("🆕 新新闻:", title)

        analysis = analyze_news(title, news["summary"])

        message = f"""
🧠 *智库分析报告*

{analysis}

🔗 [原文链接]({news["link"]})
"""

        send_telegram(message, news["image"])

        sent_titles.add(title)
        save_sent(sent_titles)

        print("✅ 完成一条，等待下一轮")
        return   # 👉 每轮只发1条


# ========= 主循环 =========
if __name__ == "__main__":
    print("🚀 系统启动成功")

    while True:
        try:
            run()
        except Exception as e:
            print("❌ 主循环错误:", e)

        print("⏳ 等待60秒...\n")
        time.sleep(60)
