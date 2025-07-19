from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import logging
import random
import threading
import time

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен бота
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("Токен бота не найден!")
    exit(1)

# Загрузка мотивационных фраз
def load_quotes():
    try:
        with open("quotes.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Ошибка загрузки цитат: {e}")
        return [
            "Если нет ветра, берись за весла.",
            "Даже самый длинный путь начинается с первого шага."
        ]

MOTIVATIONAL_PHRASES = load_quotes()

# Создаем Flask-приложение
app = Flask(__name__)

# Инициализация бота
application = Application.builder().token(TOKEN).build()

# Обработчики команд
async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Я твой мотивационный бот. Напиши /quote чтобы получить случайную цитату."
    )

async def quote(update: Update, context):
    await update.message.reply_text(random.choice(MOTIVATIONAL_PHRASES))

async def echo(update: Update, context):
    await update.message.reply_text("Напиши /quote чтобы получить мотивационную цитату")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("quote", quote))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Функция для запуска Long Polling в отдельном потоке
def run_polling():
    logger.info("Запуск Long Polling в фоновом режиме...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        close_loop=False
    )

# Вебхук для Render
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.update_queue.put(update)
    return 'ok', 200

# Эндпоинт для поддержания активности
@app.route('/')
def wakeup():
    return "Бот активен", 200

# Запуск приложения
if __name__ == '__main__':
    # Запускаем Long Polling в отдельном потоке
    polling_thread = threading.Thread(target=run_polling)
    polling_thread.daemon = True
    polling_thread.start()

    # Запускаем Flask-сервер
    app.run(host='0.0.0.0', port=10000)
