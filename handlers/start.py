from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
from database import db as db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

ASK_NAME = 1

async def start(update, context):
    user_id = update.effective_user.id
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
    res = cursor.fetchone()

    keyboard = [
        [InlineKeyboardButton("📅 Посмотреть задачи", callback_data='today')],
        [InlineKeyboardButton("✅ Отметить задачу", callback_data='done')],
        [InlineKeyboardButton("📈 Проверить прогресс", callback_data='progress')],
        [InlineKeyboardButton("📊 Скачать отчёт", callback_data='report')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if res:
        await update.message.reply_text(
            f"👋 С возвращением, {res[0]}!\n\nНажми на кнопку, чтобы начать:",
            reply_markup=reply_markup
        )
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

    keyboard = [
        [InlineKeyboardButton("📅 Посмотреть задачи", callback_data='today')],
        [InlineKeyboardButton("✅ Отметить задачу", callback_data='done')],
        [InlineKeyboardButton("📈 Проверить прогресс", callback_data='progress')],
        [InlineKeyboardButton("📊 Скачать отчёт", callback_data='report')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Спасибо, {name}! 🎉 Нажми на кнопку, чтобы начать:",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)]},
    fallbacks=[]
)
