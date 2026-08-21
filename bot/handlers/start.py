import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes, CommandHandler, ApplicationHandlerStop

MINI_APP_URL = os.getenv("MINI_APP_URL", "https://telegram-group-manager-bot-iota.vercel.app")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 باز کردن SectorLand Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]
    ])
    await update.effective_message.reply_text(
        "🌐 به iSectorLand خوش اومدی ✨\n\n"
        "از اینجا می‌تونی وارد مینی‌اپ بشی و امکانات حساب، اقتصاد و مدیریت SectorLand رو باز کنی.",
        reply_markup=keyboard,
    )
    raise ApplicationHandlerStop()


start_handler = CommandHandler("start", start)
