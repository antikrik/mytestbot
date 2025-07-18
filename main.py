
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7980220013:AAG4sdkkmxDOk6ul3iwme18941vV8ZmcmaE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, мой хозяин! Я на связи 💪")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ты красавчик, я рядом. Всегда.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()
