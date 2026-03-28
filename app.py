import requests
import feedparser
import json
import os
import time
from datetime import datetime
from openai import OpenAI

# ========= 配置 =========
TELEGRAM_TOKEN = "你的token"
CHAT_ID = "你的chat_id"
OPENAI_API_KEY = "你的key"

client = OpenAI(api_key=OPENAI_API_KEY)

RSS_LIST = [
    "https://www.rand.org/rss.xml",
    "https://www.cfr.org/rss.xml",
    "https://carnegieendowment.org/rss.xml",
    "https://www.brookings.edu/feed/",
    "https://www.csis.org/rss.xml",
    "https://warontherocks.com/feed/"
]

HISTORY_FILE = "sent_news.json"
DATE_FILE = "last_date.txt"

# ========= 日志 =========
def log(msg):
    print(f"[{datetime.now()}] {msg}")

# ========= 每日清理 =========
def check_new_day():
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(DATE_FILE):
        with open(DATE_FILE, "r") as f:
            last = f.read().strip()

        if last != today:
            log("🧹 新的一天，清空缓存")
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)

    with open(DATE_FILE, "w") as f:
        f.write(today)

# ========= 去重 =========
def load_sent():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_sent(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data)[-100:], f)

# ========= 发送 =========
def send_telegram(text):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"
            }
        )
        log(f"📤 Telegram状态: {res.status_code}")
        log(f"📤 返回: {res.text}")
    except Exception as e:
        log(f"❌ Telegram错误: {e}")

# ========= AI分析 =========
def analyze(title, summary):
    log("🧠 AI分析中...")

    prompt = f"""
你是顶级智库分析师。

标题: {title}
内容: {summary}

输出：
1. 中文翻译
2. 核心观点（1句话）
3. 战略意义
4. 影响分析
5. 趋势判断

并给出评分：
重要性: X/10
"""

    try:
        start = time.time()

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        cost = round(time.time() - start, 2)
        log(f"⏱ AI耗时: {cost}s")

        content = res.choices[0].message.content

        # 提取评分
        import re
        score = 0
        match = re.search(r"(\d+)/10", content)
        if match:
            score = int(match.group(1))

        return content, score

    except Exception as e:
        log(f"💥 AI错误: {e}")
        return None, 0

# ========= 抓取 =========
def fetch_news():
    log("🌍 抓取智库内容...")

    results = []

    for rss in RSS_LIST:
        feed = feedparser.parse(rss)

        for entry in feed.entries[:3]:
            results.append({
                "title": entry.title,
                "summary": entry.summary if "summary" in entry else "",
                "link": entry.link
            })

    log(f"📊 获取 {len(results)} 条")
    return results

# ========= 主逻辑 =========
def run_once():
    log("🚀 系统启动")

    check_new_day()

    sent = load_sent()
    news_list = fetch_news()

    for news in news_list:
        title = news["title"]

        if title in sent:
            continue

        log(f"🆕 新内容: {title}")

        analysis, score = analyze(title, news["summary"])

        if not analysis:
            log("❌ AI失败，跳过")
            return

        log(f"📊 评分: {score}")

        if score < 5:
            log("⏭ 分数太低，跳过")
            continue

        message = f"""
🧠 *智库情报*

{analysis}

🔗 {news["link"]}
"""

        send_telegram(message)

        sent.add(title)
        save_sent(sent)

        log("✅ 完成本轮")
        return

    log("📭 没有可发送内容")

# ========= 入口 =========
if __name__ == "__main__":
    try:
        run_once()
    except Exception as e:
        log(f"💥 系统错误: {e}")
