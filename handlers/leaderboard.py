from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_leaderboard_data, get_level_name


async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    leaderboard = get_leaderboard_data(top_n=15)

    if not leaderboard:
        msg = "Пока нет данных для лидерборда 😅"
        if query:
            await query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return

    text = "🏆 Лидерборд Рамадана 🏆\n\n"
    for entry in leaderboard:
        text += f"{entry['rank']}. {entry['name']} — {entry['xp']} XP, {entry['level_name']}\n"

    text += "\n🎁 Внимание! Первые 3 места получат приз — «Иштихон плов» full комплект! 🍽️\n"
    text += "Старайтесь выполнять задачи ежедневно и повышать свой XP! 💪"

    if query:
        await query.message.reply_text(text)
    else:
        await update.message.reply_text(text)
