from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает любые непонятные или неизвестные сообщения
    и показывает главное меню с кнопками.
    """
    text = "❓ Я не понимаю это сообщение. Используй кнопки ниже для навигации:"

    keyboard = [
        [InlineKeyboardButton("📅 Посмотреть задачи", callback_data="today")],
        [InlineKeyboardButton("✅ Отметить задачу", callback_data="done")],
        [InlineKeyboardButton("📈 Проверить прогресс", callback_data="progress")],
        [InlineKeyboardButton("📊 Скачать отчёт", callback_data="report")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
