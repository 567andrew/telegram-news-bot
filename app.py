import time
import requests
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def main():
    print("🔥 Bot started")

    while True:
        try:
            print("📡 sending test message...")
            send_msg("hello from render 🚀")
            time.sleep(30)
        except Exception as e:
            print("❌ error:", e)
            time.sleep(10)

if __name__ == "__main__":
    main()
