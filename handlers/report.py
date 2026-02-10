import tempfile
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from openpyxl import Workbook
from database import db as db


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