import time
import requests
import feedparser
import json
import os
import sys
from datetime import datetime
from openai import OpenAI

# ========= ✅ 强制UTF-8（关键修复）=========
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

# ========= 配置 =========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ========= 智库RSS =========
RSS_LIST = [
    "https://www.brookings.edu/feed/",
    "https://carnegieendowment.org/rss/all.xml",
    "https://www.csis.org/analysis/feed",
]

# ========= 缓存 =========
CACHE_FILE = "sent_cache.json"

def load_cache():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"date": "", "titles": []}

def save_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def is_sent(title):
    cache = load_cache()
    today = datetime.now().strftime("%Y-%m-%d")

    if cache["date"] != today:
        return False

    return title in cache["titles"]

def mark_sent(title):
    cache = load_cache()
    today = datetime.now().strftime("%Y-%m-%d")

    if cache["date"] != today:
        cache = {"date": today, "titles": []}

    cache["titles"].append(title)
    save_cache(cache)

# ========= Telegram =========
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        res = requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"
            },
            timeout=10
        )

        # ✅ 打印真实返回（关键）
        print("📤 Telegram返回:", res.text)

    except Exception as e:
        print("❌ Telegram错误:", e)

# ========= AI分析 =========
def analyze_news(title, summary):
    prompt = f"""
你是全球顶级智库分析师（兰德级别）。

请分析：

标题: {title}
内容: {summary}

输出：
1. 中文翻译
2. 核心事件
3. 深度分析
4. 战略影响
5. 趋势判断

风格：简洁、专业
"""

    try:
        start = time.time()

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        content = res.choices[0].message.content

        # ✅ 关键修复：防止中文编码崩溃
        content = content.encode("utf-8", "ignore").decode("utf-8")

        print("⏱ AI耗时:", round(time.time() - start, 2), "秒")

        return content

    except Exception as e:
        print("💥 AI错误:", e)
        return None

# ========= 抓取 =========
def fetch_news():
    results = []

    for rss in RSS_LIST:
        try:
            feed = feedparser.parse(rss)

            for entry in feed.entries[:3]:
                results.append({
                    "title": entry.title,
                    "summary": entry.summary if "summary" in entry else "",
                    "link": entry.link
                })

        except Exception as e:
            print("❌ RSS错误:", e)

    return results

# ========= 主任务 =========
def job():
    print("🌍 抓取智库内容...")

    news_list = fetch_news()
    print("📊 获取", len(news_list), "条")

    for news in news_list:
        title = news["title"]

        if is_sent(title):
            continue

        print("🆕 新内容:", title)

        analysis = analyze_news(title, news["summary"])

        if not analysis:
            print("⚠️ AI失败，跳过")
            continue

        message = f"""🧠 *智库报告*

{analysis}

🔗 [原文]({news["link"]})
"""

        send_telegram(message)

        mark_sent(title)

        time.sleep(5)

    print("✅ 本轮完成")

# ========= 主循环 =========
if __name__ == "__main__":
    print("🚀 系统启动")

    while True:
        try:
            job()
        except Exception as e:
            print("🔥 主循环错误:", e)

        print("😴 休眠60秒")
        time.sleep(60)
