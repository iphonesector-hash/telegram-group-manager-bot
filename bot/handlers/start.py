from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ApplicationHandlerStop

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات مدیریت گروه فعال شد ✨")
    raise ApplicationHandlerStop()

start_handler = CommandHandler("start", start)
