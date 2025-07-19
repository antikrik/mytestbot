from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import logging
import random
import asyncio
from threading import Thread

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

# Функция для запуска бота
def run_bot():
    logger.info("Запуск бота в режиме Long Polling...")
    application.run_polling()

# Вебхук для Render (синхронная версия)
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    asyncio.run_coroutine_threadsafe(
        application.process_update(update),
        application.updater.dispatcher.loop
    )
    return 'ok', 200

# Эндпоинт для поддержания активности
@app.route('/wakeup')
def wakeup():
    return "Бот активен", 200

# Запуск приложения
if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask-сервер
    app.run(host='0.0.0.0', port=10000)
