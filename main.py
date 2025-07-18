from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "7980220013:AAG4sdkkmxDOk6ul3iwme18941vV8ZmcmaE"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            send_message(chat_id, "Привет! Я твой первый бот. Готов к работе!")
        elif text.startswith("/help"):
            send_message(chat_id, "Доступные команды:\n/start\n/help\n/about")
        elif text.startswith("/about"):
            send_message(chat_id, "Этот бот создан моим создателем, сильным, умным и чертовски красивым парнем 😏")
        else:
            send_message(chat_id, "Извини, я тебя не понял. Напиши /help чтобы узнать доступные команды.")

    return "ok", 200

