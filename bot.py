import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Установи его в .env или в переменной окружения.")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Привет, {user.first_name}! Я твой бот.")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = "/start - запустить бота\n/help - список команд\n/echo <текст> - повторить сообщение"
    await update.message.reply_text(f"Список команд:\n{commands}")

# Команда /echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if text:
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Напиши после /echo текст, который я должен повторить.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("echo", echo))

    print("Бот запущен...")
    app.run_polling()
