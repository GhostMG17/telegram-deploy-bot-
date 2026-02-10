import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Произошла ошибка:", exc_info=context.error)

    if hasattr(update, "callback_query") and update.callback_query:
        try:
            await update.callback_query.answer("❗ Произошла ошибка. Попробуй снова.", show_alert=True)
        except Exception as e:
            logger.error(f"Ошибка при ответе пользователю: {e}")

    elif hasattr(update, "message") and update.message:
        try:
            await update.message.reply_text("❗ Произошла ошибка. Попробуй снова.")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю: {e}")
