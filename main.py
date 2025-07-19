from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = "7980220013:AAG4sdkkmxDOk6ul3iwme18941vV8ZmcmaE"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_URL = "https://mytestbot-7lzt.onrender.com"  # Ваш URL из логов

def set_webhook():
    url = f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}"
    requests.get(url)

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
            send_message(chat_id, "Привет! Я тестовый бот Ебанат Охуеевич!")
        elif text.startswith("/help"):
            send_message(chat_id, "Доступные команды:\n/start\n/help\n/about")
        elif text.startswith("/about"):
            send_message(chat_id, "Ну что ты хочешь знать обо мне, свинья кожаная? 😏")
        else:
            send_message(chat_id, "Ты ебанутый что-ли? Напиши /help чтобы узнать доступные команды.")

    return "ok", 200

if __name__ == '__main__':
    set_webhook()  # Устанавливаем вебхук при запуске
    port = int(os.environ.get("PORT", 10000))  # Используем порт 10000 для Render
    app.run(host='0.0.0.0', port=port)
