import time
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

print("Telegram News Bot started")

def bot_loop():
    while True:
        print("Bot running...")
        sys.stdout.flush()
        time.sleep(30)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def start_server():
    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

threading.Thread(target=bot_loop).start()
start_server()
