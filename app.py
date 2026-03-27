print("🔥 Andrew系统已启动")

try:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    CHAT_ID = os.environ.get("CHAT_ID")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    if not BOT_TOKEN or not CHAT_ID or not OPENAI_API_KEY:
        print("❌ 环境变量缺失")
        exit()

    print("✅ 环境变量正常")

    client = OpenAI(api_key=OPENAI_API_KEY)

except Exception as e:
    print("❌ 初始化失败:", e)
    exit()
