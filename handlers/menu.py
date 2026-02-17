from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    keyboard = [
        [InlineKeyboardButton("📅 Посмотреть задачи", callback_data='today')],
        [InlineKeyboardButton("✅ Отметить задачу", callback_data='done')],
        [InlineKeyboardButton("👤 Профиль", callback_data='profile')],
        [InlineKeyboardButton("📘 Статистика", callback_data='leaderboard')],
        [InlineKeyboardButton("📊 Скачать отчёт", callback_data='report')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🏠 Главное меню"

    if query:
        await query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
