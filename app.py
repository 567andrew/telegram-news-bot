import requests
import feedparser
import time
import os
from datetime import datetime
from openai import OpenAI

print("🔥 全球智库简报系统启动")

# ===== 环境变量 =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ===== OpenAI =====
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI 初始化成功")
except Exception as e:
    print("❌ OpenAI 初始化失败:", e)
    client = None

# ===== 核心信息源 =====
RSS_LIST = [

    # 🥇 核心
    "https://www.economist.com/latest/rss.xml",
    "https://www.ft.com/rss/home",
    "https://www.foreignaffairs.com/rss.xml",
    "https://www.brookings.edu/feed/",
    "https://www.nature.com/nature.rss",
    "https://feeds.bloomberg.com/markets/news.rss",

    # 🥈 补充
    "https://www.rand.org/pubs/rss.xml",
    "https://www.pewresearch.org/feed/",
    "https://www.oecd.org/newsroom/rss.xml",
    "https://www.theatlantic.com/feed/all/",
    "https://www.forbes.com/innovation/feed/",

    # 🥉 爆点
    "https://www.defensenews.com/arc/outboundfeeds/rss/",
    "https://www.thedrive.com/the-war-zone/rss/",
    "https://www.science.org/rss/news_current.xml",
]

sent_links = set()

# ===== 图片 =====
def get_image(title):
    keyword = title.split(" ")[0]
    return f"https://source.unsplash.com/800x600/?{keyword}"

# ===== AI生成 =====
def generate_content(title, summary):
    if not client:
        return None, None

    prompt = f"""
你是全球顶级媒体编辑（经济学人风格）。

请将以下内容转为中文简报：

标题：{title}
内容：{summary}

要求：
1. 生成一个更有洞察力的中文标题
2. 内容写成3-5段短分析
3. 每段1-2句话
4. 风格简洁、有判断

输出格式：

标题：
（新标题）

内容：
（正文）
"""

    try:
        print("🤖 AI生成中...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            timeout=20
        )

        result = response.choices[0].message.content.strip()

        # ===== 解析 =====
        if "标题：" in result and "内容：" in result:
            title_part = result.split("标题：")[1].split("内容：")[0].strip()
            content_part = result.split("内容：")[1].strip()
            return title_part, content_part
        else:
            return title, result

    except Exception as e:
        print("❌ AI错误:", e)
        return title, summary


# ===== Telegram发送 =====
def send_message(text, image_url):
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
    print("🚀 系统运行中")

    while True:
        try:
            print("🔄 新一轮开始")

            for rss in RSS_LIST:
                print("🌐 抓取:", rss)

                feed = feedparser.parse(rss)

                print("📊 数量:", len(feed.entries))

                for entry in feed.entries[:2]:
                    link = entry.link
                    title = entry.title
                    summary = entry.get("summary", "")

                    if link in sent_links:
                        continue

                    print("📰:", title)

                    ai_title, ai_content = generate_content(title, summary)

                    if not ai_content:
                        continue

                    image = get_image(title)

                    date = datetime.now().strftime("%Y-%m-%d")

                    message = f"""🧠 {ai_title}

{ai_content}

——
来源：{rss}
时间：{date}
"""

                    send_message(message, image)

                    sent_links.add(link)

                    print("✅ 已发送")

                    time.sleep(8)

            print("⏳ 等待5分钟...")
            time.sleep(300)

        except Exception as e:
            print("❌ 主循环错误:", e)
            time.sleep(30)


# ===== 启动 =====
if __name__ == "__main__":
    print("🔥 主入口启动")
    run()
