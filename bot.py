from flask import Flask, request
import requests

TOKEN = "你的BOT_TOKEN"
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

app = Flask(__name__)

@app.route("/")
def home():
    return "bot running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        reply = f"You said: {text}"

        requests.post(URL, json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"

if __name__ == "__main__":
    app.run()
