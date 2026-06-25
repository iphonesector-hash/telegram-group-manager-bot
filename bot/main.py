from telegram.ext import Application, CommandHandler
from bot.modules.locks import get_handlers

# توکن ربات — فعلاً مستقیم داخل کد
BOT_TOKEN = "8819957944:AAFVCeFQ3RXPImvhF3jjL1D418xIg9B9JLs"

async def start(update, context):
    await update.message.reply_text("ربات با موفقیت فعال شد ✨")

def main():
    # ساخت اپلیکیشن ربات
    app = Application.builder().token(BOT_TOKEN).build()

    # دستور /start
    app.add_handler(CommandHandler("start", start))

    # لود کردن هندلرهای مدیریت گروه
    for handler in get_handlers():
        app.add_handler(handler)

    print("ربات روشن شد... منتظر پیام هستم.")
    app.run_polling()

if __name__ == "__main__":
    main()
