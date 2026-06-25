from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler

# وضعیت قفل‌ها
locks = {
    "links": False,
    "photos": False,
    "videos": False,
    "stickers": False,
    "forward": False,
}

# دستور /lock
async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("مثال:\n/lock links")
        return

    lock_type = context.args[0]

    if lock_type not in locks:
        await update.message.reply_text("❌ قفل نامعتبر است.")
        return

    locks[lock_type] = True
    await update.message.reply_text(f"🔒 قفل {lock_type} فعال شد")

# دستور /unlock
async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("مثال:\n/unlock links")
        return

    lock_type = context.args[0]

    if lock_type not in locks:
        await update.message.reply_text("❌ قفل نامعتبر است.")
        return

    locks[lock_type] = False
    await update.message.reply_text(f"🔓 قفل {lock_type} غیرفعال شد")

# حذف پیام‌های خلاف قفل‌ها
async def lock_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    # لینک
    if locks["links"] and msg.entities:
        for e in msg.entities:
            if e.type in ["url", "text_link"]:
                await msg.delete()
                return

    # عکس
    if locks["photos"] and msg.photo:
        await msg.delete()
        return

    # ویدیو
    if locks["videos"] and msg.video:
        await msg.delete()
        return

    # استیکر
    if locks["stickers"] and msg.sticker:
        await msg.delete()
        return

    # فوروارد
    if locks["forward"] and msg.forward_from:
        await msg.delete()
        return

# خروجی هندلرها برای main.py
def get_handlers():
    return [
        CommandHandler("lock", lock_cmd),
        CommandHandler("unlock", unlock_cmd),
        MessageHandler(filters.ALL, lock_filter),
    ]
