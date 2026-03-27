import requests
import feedparser
import time
import os
from datetime import datetime
from openai import OpenAI

print("🔥 全球智库简报系统启动")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ===== 检查环境变量 =====
if not BOT_TOKEN or not CHAT_ID or not OPENAI_API_KEY:
    print("❌ 环境变量缺失")
else:
    print("✅ 环境变量正常")

# ===== OpenAI =====
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI 初始化成功")
except Exception as e:
    print("❌ OpenAI 初始化失败:", e)
    client = None

# ===== 稳定RSS =====
RSS_LIST = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

sent_links = set()

# ===== 图片 =====
def get_image(title):
    keyword = title.split(" ")[0]
    return f"https://source.unsplash.com/800x600/?{keyword}"

# ===== AI升级版 =====
def generate_briefing(title, summary):
    if not client:
        return title, summary

    prompt = f"""
你是全球顶级智库编辑（风格类似经济学人）。

请将以下新闻整理为中文简报：

标题：{title}
内容：{summary}

要求：

1. 生成一个更有洞察力的中文标题
2. 内容写成3-5段简短分析
3. 每段1-2句话
4. 不要列表
5. 语言简洁、有判断

输出格式：

标题：
（新标题）

内容：
（正文）
"""

    try:
        print("🤖 AI分析中...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            timeout=20
        )

        result = response.choices[0].message.content.strip()

        if "标题：" in result and "内容：" in result:
            ai_title = result.split("标题：")[1].split("内容：")[0].strip()
            ai_content = result.split("内容：")[1].strip()
            return ai_title, ai_content

        return title, result

    except Exception as e:
        print("❌ AI失败:", e)
        return title, summary


# ===== Telegram =====
def send(text, image_url):
    try:
        print("📤 发送中...")

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

        r = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "photo": image_url,
                "caption": text[:1000]
            },
            timeout=15
        )

        print("📡 返回:", r.text)

    except Exception as e:
        print("❌ 发送失败:", e)


# ===== 主程序 =====
def run():
    print("🚀 run() 已进入")

    while True:
        try:
            print("🔄 新一轮开始")

            for rss in RSS_LIST:
                print("🌐 抓取:", rss)

                feed = feedparser.parse(rss)

                print("📊 条数:", len(feed.entries))

                if not feed.entries:
                    print("⚠️ RSS为空")
                    continue

                for entry in feed.entries[:2]:
                    title = entry.title
                    link = entry.link
                    summary = entry.get("summary", "")

                    if link in sent_links:
                        continue

                    print("📰 新闻:", title)

                    ai_title, ai_content = generate_briefing(title, summary)

                    image = get_image(title)

                    date = datetime.now().strftime("%Y-%m-%d")

                    message = f"""🧠 {ai_title}

{ai_content}

——
来源：NYTimes / BBC
时间：{date}
"""

                    send(message, image)

                    sent_links.add(link)

                    print("✅ 已发送")

                    time.sleep(8)

            print("⏱️ 等待60秒...")
            time.sleep(60)

        except Exception as e:
            print("❌ 主循环错误:", e)
            time.sleep(10)


# ===== 启动 =====
if __name__ == "__main__":
    print("🔥 主入口启动")
    run()
