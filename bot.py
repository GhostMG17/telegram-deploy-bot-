import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv
from openpyxl import Workbook
import database as db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

db.init_db()
db.init_tasks()

ASK_NAME = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
    res = cursor.fetchone()

    if res:
        keyboard = [
            [InlineKeyboardButton("📅 Посмотреть задачи", callback_data='today')],
            [InlineKeyboardButton("✅ Отметить задачу", callback_data='done')],
            [InlineKeyboardButton("📈 Проверить прогресс", callback_data='progress')],
            [InlineKeyboardButton("📊 Скачать отчёт", callback_data='report')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"👋 С возвращением, {res[0]}!\n\n"
            "Нажми на кнопку, чтобы начать:\n"
            "💡 Подсказка: кнопки помогут тебе быстро управлять задачами и прогрессом.",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Привет! 👋 Пожалуйста, введи своё имя, чтобы начать использовать бота:"
        )
        return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        f"Спасибо, {name}! 🎉 Теперь твои задачи будут отслеживаться под этим именем.\n\n"
        "Нажми на кнопку, чтобы начать:",
        reply_markup=reply_markup
    )
    return ConversationHandler.END


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    msg = "\nДуховные задачи:\n"
    for name, done in db.get_progress(user_id, "spiritual"):
        status = "✅" if done else "❌"
        msg += f"{name}: {status}\n"

    msg += "\nФизические задачи:\n"
    for name, done in db.get_progress(user_id, "fitness"):
        status = "✅" if done else "❌"
        msg += f"{name}: {status}\n"

    if query:
        await query.message.reply_text(msg)
    else:  # Если вызвано через команду /today
        await update.message.reply_text(msg)




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
    elif data == "progress":
        await progress(update, context, query=query)
        return

    elif data == "report":
        await report(update, context, query=query)
        return

    if data == "confirm":
        if not selected:
            await query.edit_message_text("❗ Ты не выбрал ни одной задачи.")
            return

        for task_type, task_id in selected:
            db.mark_done(user_id, task_id, task_type)

        context.user_data["selected_tasks"] = set()
        await query.edit_message_text(f"✅ Отмечено задач: {len(selected)}")
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



async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    msg = "\nДуховные задачи:\n"
    for name, done in db.get_progress(user_id, "spiritual"):
        status = "✅" if done else "❌"
        msg += f"{name}: {status}\n"

    msg += "\nФизические задачи:\n"
    for name, done in db.get_progress(user_id, "fitness"):
        status = "✅" if done else "❌"
        msg += f"{name}: {status}\n"

    if query:
        await query.message.reply_text(msg)
    else:
        await update.message.reply_text(msg)


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    data, tasks = db.get_report_table()
    if not data:
        text = "Пока нет данных для отчёта."
        if query:
            await query.message.reply_text(text)
        else:
            await update.message.reply_text(text)
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Ramadan Progress"

    headers = ["Имя пользователя", "Дата"] + tasks + ["Все задачи выполнены?"]
    ws.append(headers)

    for row in data:
        ws.append([row.get(col) for col in headers])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        wb.save(tmp.name)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        if query:
            await query.message.reply_document(InputFile(f, filename="Ramadan_Report.xlsx"))
        else:
            await update.message.reply_document(InputFile(f, filename="Ramadan_Report.xlsx"))


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)]
    },
    fallbacks=[]
)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("done", done_buttons))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("report", report))

    print("Многопользовательский Рамадан-бот запущен...")
    app.run_polling()
