import time
import os
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "@world_monitor_news"

print("World Monitor Bot starting...")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Error sending message:", e)

def bot_loop():
    time.sleep(10)
    send_message("🌍 World Monitor Bot Online\nServer connected successfully")

    while True:
        print("Bot running...")
        time.sleep(60)

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
