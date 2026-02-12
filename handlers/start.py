from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
from database import db as db
from handlers.menu import show_menu

ASK_NAME = 1

async def start(update, context):
    user_id = update.effective_user.id
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
    res = cursor.fetchone()

    if res:
        await update.message.reply_text(
            f"👋 С возвращением, {res[0]}!"
        )
        await show_menu(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Привет! 👋 Введи своё имя, чтобы начать использовать бота:"
        )
        return ASK_NAME

async def ask_name(update, context):
    user_id = update.effective_user.id
    name = update.message.text.strip()
    db.add_user(user_id, name)

    await update.message.reply_text(f"Спасибо, {name}! 🎉")
    await show_menu(update, context)

    return ConversationHandler.END

start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)]},
    fallbacks=[]
)
