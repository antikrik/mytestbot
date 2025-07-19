from dotenv import load_dotenv
load_dotenv()

from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import logging
from telegram import Update # Импортируем здесь, чтобы избежать циклической зависимости
import random # Нам понадобится рандом для фраз!

# Включаем логирование, чтобы видеть, что происходит
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен бота из переменных окружения
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") 
if not TOKEN:
    logging.error("Токен бота не найден! Убедись, что переменная окружения TELEGRAM_BOT_TOKEN установлена.")
    exit(1)

# Здесь будут наши мотивирующие фразы
MOTIVATIONAL_PHRASES = [
    "Невозможное - это всего лишь громкое слово, которое бросают люди, которым легче жить в привычном мире, чем найти в себе силы его изменить. [Nelson Mandela]",
    "Единственный способ делать великие дела - это любить то, что ты делаешь. [Steve Jobs]",
    "Успех не окончателен, неудачи не фатальны: имеет значение лишь мужество продолжать. [Winston Churchill]"
]


# Функция-обработчик для команды /start
async def start(update: Update, context):
    """Отправляет сообщение, когда получена команда /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я твой Мотивационный Гуру. Напиши /quote, чтобы получить мощную цитату!",
    )
    logging.info(f"Получена команда /start от пользователя {user.full_name}")

# Новая функция-обработчик для команды /quote
async def quote(update: Update, context):
    """Отправляет случайную мотивирующую цитату."""
    random_quote = random.choice(MOTIVATIONAL_PHRASES) # Выбираем случайную фразу
    await update.message.reply_text(random_quote)
    logging.info(f"Отправлена цитата пользователю {update.effective_user.full_name}")

# Функция-обработчик для обычных текстовых сообщений (можно ее изменить, если захочешь)
async def echo(update: Update, context):
    """Отвечает на любое текстовое сообщение, повторяя его."""
    text = update.message.text
    await update.message.reply_text(f"Я не понял '{text}'. Если тебе нужна мотивация, напиши /quote. Если хочешь начать сначала, напиши /start.")
    logging.info(f"Получено сообщение: '{text}' от пользователя {update.effective_user.full_name}")


def main():
    """Запускает бота."""
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quote", quote)) # Новый обработчик для команды /quote

    # Добавляем обработчик для любых текстовых сообщений.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота в режиме polling. Он будет постоянно проверять новые сообщения.
    logging.info("Мотивационный бот запущен в режиме polling. Ожидаю сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()