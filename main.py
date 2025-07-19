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
import time

# Конфигурация
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("Токен бота не найден!")
    exit(1)

# Загрузка цитат с кэшированием
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

# Инициализация приложения
app = Flask(__name__)

# Конфигурация бота с увеличенными таймаутами
application = Application.builder() \
    .token(TOKEN) \
    .request(HTTPXRequest(
        connection_pool_size=2,
        connect_timeout=60,
        read_timeout=60,
        write_timeout=60,
        pool_timeout=60
    )) \
    .build()

# Улучшенные обработчики с повторением при ошибках
async def safe_send_message(update, text, parse_mode=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            if parse_mode:
                return await update.message.reply_html(text)
            return await update.message.reply_text(text)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1 + attempt * 2)
            logger.warning(f"Повтор {attempt + 1} для отправки сообщения")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_send_message(
        update,
        f"Привет, {update.effective_user.mention_html()}! Я твой мотивационный бот.",
        parse_mode="HTML"
    )

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_send_message(update, random.choice(MOTIVATIONAL_PHRASES))

# Регистрация обработчиков
handlers = [
    CommandHandler("start", start),
    CommandHandler("quote", quote),
    MessageHandler(filters.TEXT & ~filters.COMMAND, 
        lambda u, c: safe_send_message(u, "Напиши /quote для мотивации"))
]
for handler in handlers:
    application.add_handler(handler)

# Эндпоинты
@app.route('/wakeup')
def wakeup():
    return {"status": "alive"}, 200

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)
        return {"status": "ok"}, 200
    except Exception as e:
        logger.error(f"Ошибка обработки обновления: {e}")
        return {"status": "error"}, 500

# Запуск и управление жизненным циклом
async def startup():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(
        url="https://mytestbot-bwf9.onrender.com/webhook",
        max_connections=2,
        allowed_updates=["message", "callback_query"]
    )

async def shutdown():
    await application.stop()
    await application.shutdown()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(startup())
        app.run(host='0.0.0.0', port=10000)
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(shutdown())
        loop.close()
