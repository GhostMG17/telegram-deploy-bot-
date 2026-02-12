from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN
from database.db import init_db
from handlers.profile import profile
from handlers.errors import error_handler
from handlers.start import start_handler
from handlers.tasks import button_callback, done_buttons
from handlers.progress import today, progress
from handlers.report import report
from handlers.misc import unknown_message

import sys
print("Python version:", sys.version)

init_db()

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(start_handler)
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("done", done_buttons))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(CommandHandler("progress", progress))
app.add_handler(CommandHandler("report", report))
app.add_handler(CommandHandler("profile", profile))
app.add_error_handler(error_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

print("Многопользовательский Рамадан-бот запущен...")
if __name__ == "__main__":
    app.run_polling()
