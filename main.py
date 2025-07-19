from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging
import random

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

# Загрузка мотивационных фраз (ваш код без изменений)
MOTIVATIONAL_PHRASES = []
QUOTES_FILE = "quotes.txt"

def load_quotes(filename):
    phrases = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    phrases.append(line)
    except FileNotFoundError:
        logging.error(f"Файл с цитатами '{filename}' не найден!")
        return []
    except Exception as e:
        logging.error(f"Ошибка при чтении файла '{filename}': {e}")
        return []
    
    if not phrases:
        logging.warning(f"Файл с цитатами '{filename}' пуст.")
        phrases = [
            "Если нет ветра, берись за весла.",
            "Даже самый длинный путь начинается с первого шага."
        ]
    return phrases

MOTIVATIONAL_PHRASES = load_quotes(QUOTES_FILE)

# Ваши обработчики команд (без изменений)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
     await update.message.reply_html(
        f"Привет, {user.mention_html()}! Меня зовут Ирина Нечитайло, и я твой мотивационный гуру. Просто напиши /quote, и я пришлю тебе авторский мотиватор — созданный именно для тебя!",
    )

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    random_quote = random.choice(MOTIVATIONAL_PHRASES)
    await update.message.reply_text(random_quote)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"В смысле '{text}' 🙄 Если тебе нужна мотивация, значит напиши /quote. Если хочешь начать сначала, напиши /start 😏")

# Создаем Flask-приложение
app = Flask(__name__)

# Инициализация бота
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("quote", quote))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Роут для вебхука
@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    await application.process_update(update)
    return 'ok', 200

# Запуск Flask + вебхука
if __name__ == '__main__':
    # Указываем URL вашего Render-приложения (замените `your-bot-name` на реальное имя)
    WEBHOOK_URL = f"https://mytestbot-bwf9.onrender.com/webhook"
    
    # Устанавливаем вебхук
    await application.bot.set_webhook(WEBHOOK_URL)
    
    # Запускаем Flask на порту 10000 (Render требует этот порт)
    app.run(host='0.0.0.0', port=10000)