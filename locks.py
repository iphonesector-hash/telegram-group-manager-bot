from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

locks = {
    "links": False,
    "photos": False,
    "videos": False,
    "stickers": False,
    "forward": False,
}

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("مثال:\n/lock links\n/lock photos\n/lock videos")
        return

    lock_type = context.args[0]

    if lock_type not in locks:
        await update.message.reply_text("قفل نامعتبر است!")
        return

    locks[lock_type] = True
    await update.message.reply_text(f"قفل {lock_type} فعال شد 🔒")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("مثال:\n/unlock links\n/unlock photos\n/unlock videos")
        return

    lock_type = context.args[0]

    if lock_type not in locks:
        await update.message.reply_text("قفل نامعتبر است!")
        return

    locks[lock_type] = False
    await update.message.reply_text(f"قفل {lock_type} غیرفعال شد 🔓")

async def message_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg:
        return

    if locks["links"] and msg.text and ("http" in msg.text or "t.me" in msg.text):
        await msg.delete()
        return

    if locks["photos"] and msg.photo:
        await msg.delete()
        return

    if locks["videos"] and msg.video:
        await msg.delete()
        return

    if locks["stickers"] and msg.sticker:
        await msg.delete()
        return

    if locks["forward"] and msg.forward_from:
        await msg.delete()
        return

def get_handlers():
    return [
        CommandHandler("lock", lock),
        CommandHandler("unlock", unlock),
        MessageHandler(filters.ALL, message_filter),
    ]
