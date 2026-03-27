import requests
import feedparser
import time
import os
from datetime import datetime
from openai import OpenAI

# ===== 启动标志 =====
print("🔥 Andrew全球简报系统启动")

# ===== 环境变量 =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ===== OpenAI 初始化（加保护）=====
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI 初始化成功")
except Exception as e:
    print("❌ OpenAI 初始化失败:", e)
    client = None

# ===== RSS源（稳定）=====
RSS_LIST = [
    "http://feeds.reuters.com/reuters/topNews",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.economist.com/latest/rss.xml",
    "https://www.ft.com/rss/home",
    "https://www.brookings.edu/feed/"
]

# ===== 去重缓存 =====
sent_links = set()
sent_briefings = []
last_reset_day = ""

# ===== 每天清空 =====
def check_reset():
    global sent_links, sent_briefings, last_reset_day

    today = datetime.now().strftime("%Y-%m-%d")

    if last_reset_day != today:
        sent_links.clear()
        sent_briefings.clear()
        last_reset_day = today
        print("🧹 已清空缓存")

# ===== AI生成 =====
def generate_briefing(title, summary):
    if not client:
        return None

    prompt = f"""
你是顶级智库编辑，请写中文深度简报：

标题：{title}
内容：{summary}

结构如下：

【核心事件】
一句话总结

【关键事实】
3条

【深层逻辑】
为什么发生

【趋势判断】
未来变化

【影响分析】
对普通人的影响

【一句话结论】
一句总结
"""

    try:
        print("🧠 正在生成AI简报...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content.strip()

        print("📄 简报长度:", len(result))

        return result

    except Exception as e:
        print("❌ AI错误:", e)
        return None

# ===== 图片 =====
def get_image(title):
    return f"https://source.unsplash.com/800x600/?{title}"

# ===== Telegram发送 =====
def send_photo(text, image_url):
    try:
        print("📤 正在发送消息...")

        res = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "photo": image_url,
                "caption": text[:1000]
            }
        )

        print("📡 Telegram返回:", res.text)

    except Exception as e:
        print("❌ 发送失败:", e)

# ===== 主程序 =====
def run():
    print("🚀 简报系统开始运行")

    while True:
        check_reset()

        try:
            for rss in RSS_LIST:
                print(f"\n🌐 正在抓取: {rss}")

                feed = feedparser.parse(rss)

                print("📦 抓到条数:", len(feed.entries))

                for entry in feed.entries[:5]:
                    link = entry.link
                    title = entry.title
                    summary = entry.get("summary", "")

                    print("➡️ 标题:", title)

                    # ===== 去重（链接）=====
                    if link in sent_links:
                        print("⚠️ 链接重复，跳过")
                        continue

                    briefing = generate_briefing(title, summary)

                    if not briefing or len(briefing) < 80:
                        print("⚠️ AI内容无效，跳过")
                        continue

                    # ===== 内容去重 =====
                    duplicate = False
                    for b in sent_briefings[-20:]:
                        if briefing[:60] in b:
                            duplicate = True
                            break

                    if duplicate:
                        print("⚠️ 内容重复，跳过")
                        continue

                    image = get_image(title)

                    date = datetime.now().strftime("%Y-%m-%d")

                    message = f"🧠 全球简报 | {date}\n\n{briefing}"

                    send_photo(message, image)

                    sent_links.add(link)
                    sent_briefings.append(briefing)

                    print("✅ 已发送成功")

                    time.sleep(10)

        except Exception as e:
            print("❌ 主循环错误:", e)

        print("⏳ 等待10分钟...")
        time.sleep(600)


# ===== 启动 =====
if __name__ == "__main__":
    run()
