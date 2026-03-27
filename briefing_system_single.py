import requests
import feedparser
import time
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# 🌍 精选高质量源（减少噪音）
RSS_LIST = [
    "http://feeds.reuters.com/reuters/topNews",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.economist.com/latest/rss.xml",
    "https://www.ft.com/rss/home",
    "https://www.brookings.edu/feed/"
]

# ✅ 去重缓存
sent_links = set()
sent_briefings = []
last_reset_day = ""

# 🧹 每日清空
def check_reset():
    global sent_links, sent_briefings, last_reset_day

    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    today = now.strftime("%Y-%m-%d")

    if last_reset_day != today:
        sent_links.clear()
        sent_briefings.clear()
        last_reset_day = today
        print("🧹 已清空昨日数据")

# 📥 抓取
def fetch_news():
    articles = []
    for rss in RSS_LIST:
        feed = feedparser.parse(rss)
        for entry in feed.entries[:5]:
            articles.append({
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "link": entry.link
            })
    return articles

# 🔁 去重（链接）
def is_duplicate_link(link):
    return link in sent_links

# 🔁 去重（内容）
def is_duplicate_briefing(text):
    for b in sent_briefings[-20:]:
        if text[:60] in b:
            return True
    return False

# 🤖 单条深度简报（核心）
def generate_briefing(article):
    content = article["title"] + "\n" + article["summary"]

    prompt = f"""
你是全球顶级智库媒体编辑，请将以下内容整理为一篇中文“深度简报”。

要求：
- 不是新闻
- 有逻辑、有深度、有结构
- 中文输出，专业但易懂

内容：
{content}

输出结构：

【核心事件】
一句话总结

【关键事实】
3条（简洁）

【深层逻辑】
为什么发生（重点）

【趋势判断】
未来可能如何发展

【影响分析】
对普通人 / 行业意味着什么

【一句话结论】
有高度的一句话
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# 🖼️ 图片
def extract_image(entry):
    if "media_content" in entry:
        return entry.media_content[0]["url"]

    if "summary" in entry:
        imgs = re.findall(r'<img.*?src="(.*?)"', entry.summary)
        if imgs:
            return imgs[0]

    return None

def search_image(query):
    return f"https://source.unsplash.com/800x600/?{query}"

# 📤 发送
def send_photo(text, image_url):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={"chat_id": CHAT_ID, "photo": image_url, "caption": text[:1000]}
    )

# 🚀 主程序
def run():
    print("🚀 单条简报系统启动")

    while True:
        check_reset()

        try:
            for rss in RSS_LIST:
                feed = feedparser.parse(rss)

                for entry in feed.entries[:5]:
                    link = entry.link
                    title = entry.title

                    # 🔁 去重
                    if is_duplicate_link(link):
                        continue

                    print("📰 处理:", title)

                    article = {
                        "title": title,
                        "summary": entry.get("summary", "")
                    }

                    briefing = generate_briefing(article)

                    if not briefing or len(briefing) < 80:
                        continue

                    # 🔁 简报去重
                    if is_duplicate_briefing(briefing):
                        print("⚠️ 重复简报跳过")
                        continue

                    image = extract_image(entry)
                    if not image:
                        image = search_image(title)

                    date = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")

                    message = f"🧠 全球简报 | {date}\n\n{briefing}"

                    send_photo(message, image)

                    # ✅ 记录
                    sent_links.add(link)
                    sent_briefings.append(briefing)

                    print("✅ 已发送")

                    time.sleep(10)

        except Exception as e:
            print("❌ 错误:", e)

        time.sleep(600)  # 每10分钟扫描

if __name__ == "__main__":
    run()
