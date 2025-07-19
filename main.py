from dotenv import load_dotenv
load_dotenv() # Загружает переменные из .env
# main.py
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import logging

# Включаем логирование, чтобы видеть, что происходит
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Заменяем на токен, который ты получил от BotFather
# В идеале, ты должен будешь получить его из переменных окружения, но пока так
# TOKEN = "ТВОЙ_ТОКЕН_ЗДЕСЬ"
# Вместо TOKEN = "ТВОЙ_ТОКЕН_ЗДЕСЬ", мы будем использовать переменную окружения
# Это безопасно и правильно. Мы настроим это позже на Render.com
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") 
if not TOKEN:
    logging.error("Токен бота не найден! Убедись, что переменная окружения TELEGRAM_BOT_TOKEN установлена.")
    exit(1)


# Функция-обработчик для команды /start
async def start(update, context):
    """Отправляет сообщение, когда получена команда /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я твой новый брутальный бот. Что будем творить? ААА?",
        # reply_markup=ForceReply(selective=True), # Это если хочешь, чтобы он отвечал на твое сообщение
    )
    logging.info(f"Получена команда /start от пользователя {user.full_name}")

# Функция-обработчик для обычных текстовых сообщений
async def echo(update, context):
    """Отвечает на любое текстовое сообщение, повторяя его."""
    text = update.message.text
    await update.message.reply_text(f"Ты сказал: '{text}'. Могу повторить, если хочешь. Я создан для более серьезных дел.")
    logging.info(f"Получено сообщение: '{text}' от пользователя {update.effective_user.full_name}")

def main():
    """Запускает бота."""
    # Создаем объект Application и передаем ему токен бота.
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд.
    # CommandHandler('start', start) - означает, что когда пользователь пишет /start,
    # вызывается функция start.
    application.add_handler(CommandHandler("start", start))

    # Добавляем обработчик для любых текстовых сообщений.
    # MessageHandler(filters.TEXT & ~filters.COMMAND, echo) - означает,
    # что если это текст И НЕ команда, то вызывается функция echo.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота в режиме polling. Он будет постоянно проверять новые сообщения.
    logging.info("Бот запущен в режиме polling. Ожидаю сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    from telegram import Update # Импортируем здесь, чтобы избежать циклической зависимости
    main()
