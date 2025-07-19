from dotenv import load_dotenv
load_dotenv()

from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import logging
import random

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

# Обработчики команд
async def start(update, context):
    await update.message.reply_text(
        "Привет! Я твой мотивационный бот. Напиши /quote чтобы получить случайную цитату."
    )

async def quote(update, context):
    await update.message.reply_text(random.choice(MOTIVATIONAL_PHRASES))

async def echo(update, context):
    await update.message.reply_text("Напиши /quote чтобы получить мотивационную цитату")

def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quote", quote))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота в режиме Long Polling
    logger.info("Бот запущен в режиме Long Polling...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
