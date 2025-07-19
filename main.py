from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import os
import logging
import random
import asyncio
import telegram

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен бота
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logging.error("Токен бота не найден!")
    exit(1)

# Загрузка мотивационных фраз
MOTIVATIONAL_PHRASES = []
QUOTES_FILE = "quotes.txt"

def load_quotes(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"Файл с цитатами '{filename}' не найден!")
    except Exception as e:
        logging.error(f"Ошибка при чтении файла: {e}")
    return [
        "Если нет ветра, берись за весла.",
        "Даже самый длинный путь начинается с первого шага."
    ]

MOTIVATIONAL_PHRASES = load_quotes(QUOTES_FILE)

# Создаем Flask-приложение
app = Flask(__name__)

# Инициализация бота с оптимизированными настройками
application = Application.builder() \
    .token(TOKEN) \
    .request(HTTPXRequest(
        connection_pool_size=1,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30
    )) \
    .build()

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        f"Привет, {update.effective_user.mention_html()}! Я твой мотивационный бот."
    )

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(MOTIVATIONAL_PHRASES))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Напиши /quote для мотивации!")

# Добавляем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("quote", quote))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Роут для пробуждения сервиса
@app.route('/wakeup')
def wakeup():
    return "OK", 200

# Роут для вебхука с обработкой ошибок
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)
        return 'ok', 200
    except telegram.error.TimedOut:
        logging.warning("Таймаут соединения, повторяю запрос...")
        await asyncio.sleep(1)
        return await webhook()
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        return 'error', 500

# Асинхронная инициализация
async def setup():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(
        url="https://mytestbot-bwf9.onrender.com/webhook",
        max_connections=1
    )

# Запуск приложения
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup())
    
    try:
        app.run(host='0.0.0.0', port=10000)
    finally:
        loop.run_until_complete(application.stop())
