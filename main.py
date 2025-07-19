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

MOTIVATIONAL_PHRASES = [] # Теперь это будет пустой список, который мы заполним из файла
QUOTES_FILE = "quotes.txt" # Имя файла с цитатами

# Функция для загрузки фраз из файла
def load_quotes(filename):
    phrases = []
    try:
        with open(filename, "r", encoding="utf-8") as f: # Открываем файл для чтения
            for line in f:
                line = line.strip() # Удаляем лишние пробелы и символы новой строки
                if line: # Проверяем, что строка не пустая
                    phrases.append(line)
    except FileNotFoundError:
        logging.error(f"Файл с цитатами '{filename}' не найден!")
        return [] # Возвращаем пустой список, если файл не найден
    except Exception as e:
        logging.error(f"Ошибка при чтении файла '{filename}': {e}")
        return []
    
    if not phrases: # Если файл пустой или все строки были пустыми
        logging.warning(f"Файл с цитатами '{filename}' пуст или содержит только пустые строки.")
    
    return phrases

# Загружаем фразы при старте бота
MOTIVATIONAL_PHRASES = load_quotes(QUOTES_FILE)

# Если фразы не загрузились, добавим дефолтные, чтобы бот не был пустым
if not MOTIVATIONAL_PHRASES:
    logging.warning("Фразы не загружены из файла. Используются дефолтные фразы.")
    MOTIVATIONAL_PHRASES = [
        "Если нет ветра, берись за весла. Это дефолтная фраза.",
        "Даже самый длинный путь начинается с первого шага. Это тоже дефолтная фраза."
    ]

# ... (остальной код остается без изменений, включая функции start, quote, echo и main)


# Функция-обработчик для команды /start
async def start(update: Update, context):
    """Отправляет сообщение, когда получена команда /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Меня зовут Ирина Нечитайло, и я твой мотивационный гуру. Просто напиши /quote, и я пришлю тебе авторский мотиватор — созданный именно для тебя!",
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
    await update.message.reply_text(f"В смысле '{text}'? Если тебе нужна мотивация, значит напиши /quote. Если хочешь начать сначала, напиши /start.")
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