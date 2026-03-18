def extract_news_brief(text):

    sentences = re.split(r'[.!?。]', text)

    important = []

    keywords = [
        "killed","attack","airstrike","missile",
        "announced","said","warned","confirmed",
        "accused","launched","reported","dead",
        "strike","explosion"
    ]

    for s in sentences:

        s = s.strip()

        if len(s) < 25:
            continue

        score = 0

        for k in keywords:
            if k in s.lower():
                score += 1

        important.append((score, s))

    important.sort(reverse=True)

    selected = [s for score,s in important[:3]]

    if not selected:
        selected = sentences[:3]

    return "。 ".join(selected) + "。"
