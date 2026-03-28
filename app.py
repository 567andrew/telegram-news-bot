def run_once():
    news_list = fetch_news()

    if not news_list:
        print("❌ 没抓到新闻")
        return

    news = news_list[0]

    print("🔥 强制发送:", news["title"])

    message = f"""
测试新闻：

{news["title"]}

{news["link"]}
"""

    send_telegram(message, news["image"])
