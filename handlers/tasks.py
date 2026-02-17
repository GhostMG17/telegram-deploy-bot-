from database.db import add_xp
from handlers.progress import today
from handlers.report import report
from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import db as db
from handlers.profile import profile
from handlers.leaderboard import leaderboard_handler


async def done_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    context.user_data["selected_tasks"] = set()
    keyboard = []

    for task_id, name in db.get_tasks("spiritual"):
        if not db.is_task_done_today(user_id, task_id, "spiritual"):
            keyboard.append([
                InlineKeyboardButton("❌ " + name, callback_data=f"toggle:spiritual:{task_id}")
            ])

    for task_id, name in db.get_tasks("fitness"):
        if not db.is_task_done_today(user_id, task_id, "fitness"):
            keyboard.append([
                InlineKeyboardButton("❌ " + name, callback_data=f"toggle:fitness:{task_id}")
            ])

    if not keyboard:
        text = "🎉 Все задачи на сегодня уже выполнены!"
        if query:
            await query.message.reply_text(text)
        else:
            await update.message.reply_text(text)
        return

    keyboard.append([InlineKeyboardButton("✅ Подтвердить", callback_data="confirm")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "Выбери выполненные задачи, нажимая на них. ✅ Подтверждение внизу:"
    if query:
        await query.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)



async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    selected = context.user_data.setdefault("selected_tasks", set())

    if data == "today":
        await today(update, context, query=query)
        return
    elif data == "done":
        await done_buttons(update, context, query=query)
        return

    elif data == "report":
        await report(update, context, query=query)
        return

    elif data == "profile":
        await profile(update, context, query=query)
        return

    elif data == "leaderboard":
        await leaderboard_handler(update, context, query=query)
        return

    elif data == "menu":
        from handlers.menu import show_menu
        await show_menu(update, context, query=query)
        return

    if data == "confirm":
        if not selected:
            await query.edit_message_text("❗ Ты не выбрал ни одной задачи.")
            return

        XP_PER_TASK = {
            "spiritual": 10,
            "fitness": 5
        }

        total_xp = 0

        for task_type, task_id in selected:
            db.mark_done(user_id, task_id, task_type)
            total_xp += XP_PER_TASK.get(task_type, 0)

        new_xp, new_level = add_xp(user_id, total_xp)

        context.user_data["selected_tasks"] = set()

        await query.edit_message_text(
            f"✅ Отмечено задач: {len(selected)}\n"
            f"✨ +{total_xp} XP\n"
            f"🏅 Уровень: {new_level}"
        )
        return

    if data.startswith("toggle:"):
        try:
            _, task_type, task_id = data.split(":")
            task_id = int(task_id)
        except ValueError:
            await query.answer("❗ Ошибка в данных кнопки", show_alert=True)
            return

        key = (task_type, task_id)
        if key in selected:
            selected.remove(key)
        else:
            selected.add(key)

        keyboard = []

        for t_id, name in db.get_tasks("spiritual"):
            if not db.is_task_done_today(user_id, t_id, "spiritual"):
                prefix = "✅ " if ("spiritual", t_id) in selected else "❌ "
                keyboard.append([InlineKeyboardButton(f"{prefix}{name}", callback_data=f"toggle:spiritual:{t_id}")])

        for t_id, name in db.get_tasks("fitness"):
            if not db.is_task_done_today(user_id, t_id, "fitness"):
                prefix = "✅ " if ("fitness", t_id) in selected else "❌ "
                keyboard.append([InlineKeyboardButton(f"{prefix}{name}", callback_data=f"toggle:fitness:{t_id}")])

        keyboard.append([InlineKeyboardButton("✅ Подтвердить", callback_data="confirm")])

        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await query.answer("❗ Неизвестная кнопка", show_alert=True)