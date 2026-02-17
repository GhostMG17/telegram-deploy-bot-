from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db as db
from database.db import calculate_level, get_user_xp, get_today_progress, LEVELS

LEVEL_EMOJIS = {
    1: "🌱 Начало",
    2: "🔥 В пути",
    3: "💪 Укрепился",
    4: "🏆 Стабильность",
    5: "👑 Мастер Рамадана"
}

XP_PER_TASK = {
    "spiritual": 10,
    "fitness": 5
}


def xp_bar(xp, level):
    thresholds = {lvl: th for lvl, th in LEVELS}
    if level < LEVELS[-1][0]:
        next_xp = thresholds[level + 1]
    else:
        next_xp = thresholds[level]

    if next_xp == 0:
        next_xp = 1

    progress = int((xp / next_xp) * 10)
    bar = "▓" * min(progress, 10) + "░" * max(10 - progress, 0)

    if level == LEVELS[-1][0]:
        return f"{bar} (максимальный уровень)"
    return f"{bar} ({xp}/{next_xp} XP)"


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id

    xp, _ = get_user_xp(user_id)
    level = calculate_level(xp)
    bar = xp_bar(xp, level)

    done_spiritual, total_spiritual, done_fitness, total_fitness = db.get_today_progress(user_id)

    xp_spiritual = done_spiritual * XP_PER_TASK["spiritual"]
    xp_fitness = done_fitness * XP_PER_TASK["fitness"]
    xp_today = xp_spiritual + xp_fitness

    text = (
        f"👤 Профиль пользователя\n\n"
        f"💎 Текущий уровень: {level}\n"
        f"{bar}\n\n"
        f"📊 Прогресс сегодня:\n"
        f"Духовные задачи: {done_spiritual}/{total_spiritual} ✅ "
        f"({done_spiritual} × {XP_PER_TASK['spiritual']} XP = +{xp_spiritual} XP)\n"
        f"Физические задачи: {done_fitness}/{total_fitness} ✅ "
        f"({done_fitness} × {XP_PER_TASK['fitness']} XP = +{xp_fitness} XP)\n"
        f"💫 XP сегодня: +{xp_today} XP\n\n"
        f"🏅 Уровни и награды:\n"
        + "\n".join(f"{lvl} — {emoji}" for lvl, emoji in LEVEL_EMOJIS.items())
    )

    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
