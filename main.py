from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest
import os
import logging
import random
import asyncio

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
def load_quotes(filename="quotes.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
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

# Инициализация бота с увеличенными таймаутами
application = Application.builder() \
    .token(TOKEN) \
    .request(HTTPXRequest(
        connection_pool_size=10,  # Увеличено количество соединений
        connect_timeout=30,
        read_timeout=30,
        write_timeout=30,
        pool_timeout=30
    )) \
    .build()

# Простые обработчики команд
async def start(update: Update, context):
    try:
        await update.message.reply_text(
            "Привет! Я твой мотивационный бот. Напиши /quote чтобы получить случайную цитату."
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")

async def quote(update: Update, context):
    try:
        quote = random.choice(MOTIVATIONAL_PHRASES)
        await update.message.reply_text(quote)
    except Exception as e:
        logger.error(f"Ошибка отправки цитаты: {e}")

async def echo(update: Update, context):
    try:
        await update.message.reply_text("Напиши /quote чтобы получить мотивационную цитату")
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("quote", quote))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Вебхук с базовой обработкой ошибок
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)
        return 'ok', 200
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
        return 'error', 500

# Эндпоинт для поддержания активности
@app.route('/wakeup')
def wakeup():
    return 'ok', 200

# Запуск приложения
if __name__ == '__main__':
    async def setup():
        await application.initialize()
        await application.start()
        await application.bot.set_webhook(
            url="https://mytestbot-bwf9.onrender.com/webhook",
            max_connections=10,  # Увеличено максимальное количество соединений
            allowed_updates=["message"]
        )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(setup())
        app.run(host='0.0.0.0', port=10000)
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}")
    finally:
        loop.run_until_complete(application.stop())
        loop.close()
