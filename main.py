from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging
import random
import asyncio
from threading import Thread
from queue import Queue

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
MOTIVATIONAL_PHRASES = [
    "Если нет ветра, берись за весла.",
    "Даже самый длинный путь начинается с первого шага."
]

# Создаем Flask-приложение
app = Flask(__name__)

# Очередь для обновлений
update_queue = Queue()

# Инициализация бота
application = Application.builder().token(TOKEN).build()

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я твой мотивационный бот. Напиши /quote чтобы получить случайную цитату."
    )

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(MOTIVATIONAL_PHRASES))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши /quote чтобы получить мотивационную цитату")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("quote", quote))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Функция для обработки обновлений из очереди
async def process_updates():
    while True:
        update = update_queue.get()
        await application.process_update(update)
        update_queue.task_done()

# Вебхук для Render
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    update_queue.put(update)
    return 'ok', 200

# Эндпоинт для поддержания активности
@app.route('/wakeup')
def wakeup():
    return "Бот активен", 200

# Запуск приложения
if __name__ == '__main__':
    # Запускаем обработку обновлений в фоновом режиме
    Thread(target=lambda: asyncio.run(process_updates()), daemon=True).start()
    
    # Запускаем Flask-сервер
    app.run(host='0.0.0.0', port=10000)
