from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler

locks = {
    "links": False,
    "photos": False,
    "videos": False,
    "stickers": False,
    "forward": False,
}

async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text("مثال:\n/lock links")
        return

    lock_type = context.args[0]

    if lock_type not in locks:
        await update.message.reply_text("❌ قفل نامعتبر است.")
        return

    locks[lock_type] = True
    await update.message.reply_text(f"🔒 قفل {lock_type} فعال شد")

async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text("مثال:\n/unlock links")
        return

    lock_type = context.args[0]

    if lock_type not in locks:
        await update.message.reply_text("❌ قفل نامعتبر است.")
        return

    locks[lock_type] = False
    await update.message.reply_text(f"🔓 قفل {lock_type} غیرفعال شد")

async def lock_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    msg = update.message

    if locks["links"] and msg.entities:
        for e in msg.entities:
            if e.type in ["url", "text_link"]:
                try:
                    await msg.delete()
                except:
                    pass
                return

    if locks["photos"] and msg.photo:
        try:
            await msg.delete()
        except:
            pass
        return

    if locks["videos"] and msg.video:
        try:
            await msg.delete()
        except:
            pass
        return

    if locks["stickers"] and msg.sticker:
        try:
            await msg.delete()
        except:
            pass
        return

    if locks["forward"] and (msg.forward_from or msg.forward_from_chat):
        try:
            await msg.delete()
        except:
            pass
        return

def get_handlers():
    return [
        CommandHandler("lock", lock_cmd),
        CommandHandler("unlock", unlock_cmd),
        MessageHandler(filters.ALL, lock_filter),
    ]
