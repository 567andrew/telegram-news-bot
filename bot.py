import time
import requests
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = "8627523908:AAHF2jOi7YJLb-ckZZ_gQ9VVeMU_iSXbO30"
CHAT_ID = "@world_monitor_news"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

print("Telegram News Bot started")

def bot_loop():
    send_message("🌍 World Monitor Bot Online\nRender server connected.")
    while True:
        try:
            print("Bot running...")
            sys.stdout.flush()
            time.sleep(60)
        except Exception as e:
            print("Error:", e)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def start_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=bot_loop).start()
start_server()
