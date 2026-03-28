import time
import requests
import feedparser
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

sent_titles = set()

# ========= 发送消息 =========
def send_telegram(text, image=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    if image:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "caption": text,
                    "parse_mode": "Markdown"
                },
                files=None,
                json=None,
                params={"photo": image}
            )
            return
        except:
            pass

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })


# ========= AI分析 =========
def analyze_news(title, summary):
    prompt = f"""
你是一个国际智库分析师（类似兰德公司）。

请对这条新闻做【战略级分析】：

标题: {title}
内容: {summary}

要求输出：

1. 中文翻译（准确）
2. 核心事件（1句话）
3. 深度分析（发生了什么，本质是什么）
4. 影响评估（对国际局势的影响）
5. 关键判断（未来可能如何发展）

风格：
- 专业
- 简洁
- 像情报报告
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
    results = []

    for rss in RSS_LIST:
        feed = feedparser.parse(rss)

        for entry in feed.entries[:3]:
            title = entry.title
            summary = entry.summary if "summary" in entry else ""
            link = entry.link

            image = None
            if "media_content" in entry:
                image = entry.media_content[0]["url"]

            results.append({
                "title": title,
                "summary": summary,
                "link": link,
                "image": image
            })

    return results


# ========= 主流程 =========
def run():
    news_list = fetch_news()

    for news in news_list:
        if news["title"] in sent_titles:
            continue

        sent_titles.add(news["title"])

        print("处理:", news["title"])

        analysis = analyze_news(news["title"], news["summary"])

        message = f"""
🧠 *智库分析报告*

{analysis}

🔗 [原文链接]({news["link"]})
"""

        send_telegram(message, news["image"])

        time.sleep(3)


# ========= 主循环 =========
if __name__ == "__main__":
    print("🚀 启动智库系统")

    for i in range(10):
        print(f"第{i+1}轮扫描")

        try:
            run()
        except Exception as e:
            print("错误:", e)

        time.sleep(60)
