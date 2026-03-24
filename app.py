import os

print("🔥 程序启动了")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)
print("OPENAI:", OPENAI_API_KEY)

if not BOT_TOKEN:
    print("❌ BOT_TOKEN 没设置")
    exit()
