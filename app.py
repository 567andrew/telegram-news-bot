import requests
import feedparser
import json
import os
from datetime import datetime
from openai import OpenAI

# ========= 配置 =========
TELEGRAM_TOKEN = "你的token"
CHAT_ID = "你的chat_id"
OPENAI_API_KEY = "你的key"

client = OpenAI(api_key=OPENAI_API_KEY)

# ========= 智库RSS =========
RSS_LIST = [
    "https://www.rand.org/rss.xml",
    "https://www.cfr.org/rss.xml",
    "https://carnegieendowment.org/rss.xml",
    "https://www.brookings.edu/feed/",
    "https://www.csis.org/rss.xml",
    "https://warontherocks.com/feed/"
]

# ========= 缓存 =========
HISTORY_FILE = "sent_news.json"
DATE_FILE = "last_date.txt"
MAX_HISTORY = 100

# ========= 日期检查 =========
def check_new_day():
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(DATE_FILE):
        with open(DATE_FILE, "r") as f:
            last_date = f.read().strip()

        if last_date != today:
            print("🧹 新的一天，清空缓存")
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
    data = list(data)[-MAX_HISTORY:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

# ========= 发送 =========
def send_telegram(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"
            }
        )
        print("✅ 发送成功")
    except Exception as e:
        print("❌ 发送失败:", e)

# ========= AI分析 =========
def analyze_thinktank(title, summary, source):
    print("🧠 AI分析中...")

    prompt = f"""
你是全球顶级智库分析师（兰德级别）。

来源: {source}
标题: {title}
内容: {summary}

输出：

【1】中文翻译（准确）
【2】核心观点（1句话）
【3】关键信息（3点）
【4】战略本质（本质逻辑）
【5】国家利益分析（谁受益/受损）
【6】风险与机会
【7】趋势判断

要求：
- 像情报报告
- 简洁有力
- 不废话
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ AI分析失败: {e}"

# ========= 抓取 =========
def fetch_news():
    print("🌍 抓取智库内容...")

    results = []

    for rss in RSS_LIST:
        feed = feedparser.parse(rss)

        for entry in feed.entries[:3]:
            results.append({
                "title": entry.title,
                "summary": entry.summary if "summary" in entry else "",
                "link": entry.link,
                "source": rss
            })

    print(f"📊 获取 {len(results)} 条")
    return results

# ========= 主逻辑 =========
def run_once():
    check_new_day()

    sent_titles = load_sent()
    news_list = fetch_news()

    for news in news_list:
        title = news["title"]

        if title in sent_titles:
            continue

        print("🆕 新内容:", title)

        analysis = analyze_thinktank(
            title,
            news["summary"],
            news["source"]
        )

        message = f"""
🧠 *全球智库情报*

{analysis}

🔗 原文:
{news["link"]}
"""

        send_telegram(message)

        sent_titles.add(title)
        save_sent(sent_titles)

        print("✅ 完成本轮任务")
        return

    print("⚠️ 今日暂无新内容")

# ========= 入口 =========
if __name__ == "__main__":
    print("🚀 智库系统启动:", datetime.now())

    try:
        run_once()
    except Exception as e:
        print("💥 错误:", e)
