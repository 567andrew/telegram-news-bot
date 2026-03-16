def news_loop():

    print("GLOBAL RADAR STARTED")

    while True:

        try:

            for source,url in NEWS_FEEDS.items():

                print("Scanning:",source)

                feed=feedparser.parse(url)

                if not feed.entries:
                    continue

                entry = feed.entries[0]

                if entry.link not in posted:

                    title = entry.title

                    msg=f"""
🌍 全球新闻

标题
{title}

WHO
Unknown

WHAT
{title}

WHERE
Global

WHEN
Latest

WHY
Developing

SRC
{source}
"""

                    send_message(msg)

                    posted.add(entry.link)

                time.sleep(1)

        except Exception as e:

            print("ERROR:",e)

        time.sleep(300)
