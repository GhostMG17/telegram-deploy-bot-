from telegram import Update
from telegram.ext import ContextTypes
from database import db as db


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
    else:
        await update.message.reply_text(msg)

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