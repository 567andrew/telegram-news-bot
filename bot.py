import time
import sys

print("Telegram News Bot started")

while True:
    try:
        print("Bot running...")
        sys.stdout.flush()
        time.sleep(30)
    except Exception as e:
        print("Error:", e)
